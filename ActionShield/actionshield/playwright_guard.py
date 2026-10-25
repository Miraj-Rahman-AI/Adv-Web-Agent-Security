from inspect import isawaitable
from urllib.parse import urlsplit
from typing import Any

from .engine import ActionShield, ApprovalCallback
from .models import (
    ActionImpact,
    ActionRequest,
    ActionType,
    DecisionStatus,
)


def canonical_url(url: str) -> tuple:
    """Normalize a URL for in-memory navigation grants."""

    parsed = urlsplit(url)

    return (
        parsed.scheme.lower(),
        (parsed.hostname or "").lower(),
        parsed.port,
        parsed.path or "/",
        parsed.query,
    )


class GuardedPage:
    """
    A restricted wrapper around a Playwright Page.

    Give the agent this wrapper instead of the raw Page object.
    """

    def __init__(
        self,
        page: Any,
        shield: ActionShield,
        approval_callback: ApprovalCallback | None = None,
    ):
        self.__page = page
        self._shield = shield
        self._approval_callback = approval_callback
        self._navigation_grants: set[tuple] = set()
        self._guard_installed = False

    def _current_url(self) -> str | None:
        url = self.__page.url

        if url.startswith(("http://", "https://")):
            return url

        return None

    async def _ask_approval(
        self,
        request: ActionRequest,
        decision,
    ) -> bool:
        if self._approval_callback is None:
            return False

        result = self._approval_callback(
            request,
            decision,
        )

        if isawaitable(result):
            result = await result

        return bool(result)

    async def install_navigation_guard(self) -> None:
        """Guard navigations and redirects for this page."""

        if self._guard_installed:
            return

        async def route_handler(route):
            browser_request = route.request

            if not browser_request.is_navigation_request():
                await route.continue_()
                return

            request = ActionRequest(
                action_type=ActionType.NAVIGATE,
                current_url=self._current_url(),
                destination_url=browser_request.url,
                description="Browser navigation or redirect",
            )

            decision = self._shield.evaluate(request)

            if decision.status == DecisionStatus.DENY:
                self._shield.audit.record(
                    request,
                    "blocked_navigation",
                    decision.reason,
                )

                await route.abort("blockedbyclient")
                return

            # An explicit goto() has already passed the
            # approval stage before its callback executes.
            preapproved = (
                canonical_url(browser_request.url)
                in self._navigation_grants
            )

            if (
                decision.status
                == DecisionStatus.REQUIRES_APPROVAL
                and not preapproved
            ):
                approved = await self._ask_approval(
                    request,
                    decision,
                )

                if not approved:
                    self._shield.audit.record(
                        request,
                        "blocked_navigation",
                        "Navigation approval was not granted.",
                    )

                    await route.abort("blockedbyclient")
                    return

            self._shield.audit.record(
                request,
                "navigation_allowed",
                "Navigation passed the configured checks.",
            )

            await route.continue_()

        await self.__page.route(
            "**/*",
            route_handler,
        )

        self._guard_installed = True

    async def _run(
        self,
        request: ActionRequest,
        operation,
    ):
        result = await self._shield.execute(
            request,
            operation,
            approval_callback=self._approval_callback,
        )

        if not result.executed:
            raise PermissionError(
                f"ActionShield blocked "
                f"{request.action_type.value}: "
                f"{result.decision.reason}"
            )

        return result.output

    async def goto(self, url: str):
        request = ActionRequest(
            action_type=ActionType.NAVIGATE,
            current_url=self._current_url(),
            destination_url=url,
            description="Navigate to a website",
        )

        async def operation():
            grant = canonical_url(url)
            self._navigation_grants.add(grant)

            try:
                return await self.__page.goto(url)
            finally:
                self._navigation_grants.discard(grant)

        return await self._run(request, operation)

    async def click(
        self,
        selector: str,
        *,
        description: str = "Click a browser element",
        impact: ActionImpact = ActionImpact.LOW,
        target_url: str | None = None,
    ):
        request = ActionRequest(
            action_type=ActionType.CLICK,
            current_url=self._current_url(),
            destination_url=target_url,
            description=description,
            target=selector,
            impact=impact,
        )

        return await self._run(
            request,
            lambda: self.__page.locator(selector).click(),
        )

    async def fill(
        self,
        selector: str,
        value: str,
        *,
        description: str = "Fill a form field",
        impact: ActionImpact = ActionImpact.LOW,
    ):
        request = ActionRequest(
            action_type=ActionType.TYPE,
            current_url=self._current_url(),
            description=description,
            target=selector,
            impact=impact,
        )

        # The entered value is deliberately excluded from
        # the request and security audit record.
        return await self._run(
            request,
            lambda: self.__page.locator(selector).fill(value),
        )

    async def submit(
        self,
        selector: str,
        *,
        description: str = "Submit a form",
    ):
        request = ActionRequest(
            action_type=ActionType.SUBMIT,
            current_url=self._current_url(),
            description=description,
            target=selector,
            impact=ActionImpact.HIGH,
        )

        return await self._run(
            request,
            lambda: self.__page.locator(selector).click(),
        )

    async def download(self, selector: str):
        request = ActionRequest(
            action_type=ActionType.DOWNLOAD,
            current_url=self._current_url(),
            description="Download a file",
            target=selector,
            impact=ActionImpact.HIGH,
        )

        async def operation():
            async with self.__page.expect_download() as info:
                await self.__page.locator(selector).click()

            return await info.value

        return await self._run(request, operation)
