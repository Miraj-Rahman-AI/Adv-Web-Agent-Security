from inspect import isawaitable
from typing import Any, Awaitable, Callable

from .audit import AuditSink, LoggingAuditSink
from .models import (
    ActionDecision,
    ActionImpact,
    ActionRequest,
    ActionType,
    DecisionStatus,
    ExecutionResult,
)
from .policy import ActionPolicy


ApprovalCallback = Callable[
    [ActionRequest, ActionDecision],
    bool | Awaitable[bool],
]

ActionCallback = Callable[[], Any]


class ActionShield:
    """Policy enforcement for LLM-based Web Agent actions."""

    def __init__(
        self,
        policy: ActionPolicy,
        audit: AuditSink | None = None,
    ):
        self.policy = policy
        self.audit = audit or LoggingAuditSink()

    def _decision(
        self,
        status: DecisionStatus,
        reason: str,
    ) -> ActionDecision:
        return ActionDecision(
            status=status,
            reason=reason,
            policy_id=self.policy.policy_id,
        )

    def evaluate(
        self,
        request: ActionRequest,
    ) -> ActionDecision:
        """Evaluate an action without executing it."""

        if request.action_type not in self.policy.allowed_actions:
            return self._decision(
                DecisionStatus.DENY,
                f"Action '{request.action_type.value}' "
                "is not permitted by policy.",
            )

        if (
            request.action_type == ActionType.NAVIGATE
            and not request.destination_url
        ):
            return self._decision(
                DecisionStatus.DENY,
                "Navigation requires a destination URL.",
            )

        if (
            request.action_type != ActionType.NAVIGATE
            and not request.current_url
        ):
            return self._decision(
                DecisionStatus.DENY,
                "A current page URL is required for this action.",
            )

        urls = [
            ("current page", request.current_url),
            ("destination", request.destination_url),
        ]

        if not any(url for _, url in urls):
            return self._decision(
                DecisionStatus.DENY,
                "The action has no verifiable URL context.",
            )

        # Validate both the current page and any known destination.
        for label, url in urls:
            if not url:
                continue

            error = self.policy.url_error(url)

            if error:
                return self._decision(
                    DecisionStatus.DENY,
                    f"{label.capitalize()} rejected: {error}",
                )

        needs_approval = (
            request.action_type
            in self.policy.require_approval_for
            or request.impact
            in self.policy.require_approval_for_impact
        )

        if needs_approval:
            return self._decision(
                DecisionStatus.REQUIRES_APPROVAL,
                "The action requires explicit approval.",
            )

        return self._decision(
            DecisionStatus.ALLOW,
            "The action satisfies the configured policy.",
        )

    async def execute(
        self,
        request: ActionRequest,
        action: ActionCallback,
        approval_callback: ApprovalCallback | None = None,
    ) -> ExecutionResult:
        """
        Evaluate and, if authorized, execute an operation.

        Both synchronous and asynchronous action callbacks
        and approval callbacks are supported.
        """

        decision = self.evaluate(request)

        if decision.status == DecisionStatus.DENY:
            self.audit.record(
                request,
                "blocked",
                decision.reason,
            )

            return ExecutionResult(
                executed=False,
                decision=decision,
            )

        if decision.status == DecisionStatus.REQUIRES_APPROVAL:
            if approval_callback is None:
                denied = self._decision(
                    DecisionStatus.DENY,
                    "Approval is required, but no approval "
                    "callback is configured.",
                )

                self.audit.record(
                    request,
                    "blocked",
                    denied.reason,
                )

                return ExecutionResult(
                    executed=False,
                    decision=denied,
                )

            try:
                approved = approval_callback(
                    request,
                    decision,
                )

                if isawaitable(approved):
                    approved = await approved

            except Exception:
                self.audit.record(
                    request,
                    "approval_error",
                    "The approval callback raised an exception.",
                )
                raise

            if not approved:
                denied = self._decision(
                    DecisionStatus.DENY,
                    "Explicit approval was denied.",
                )

                self.audit.record(
                    request,
                    "blocked",
                    denied.reason,
                )

                return ExecutionResult(
                    executed=False,
                    decision=denied,
                )

            decision = self._decision(
                DecisionStatus.ALLOW,
                "Explicit approval granted. "
                + decision.reason,
            )

        # This is the only point where the supplied operation runs.
        try:
            output = action()

            if isawaitable(output):
                output = await output

        except Exception:
            self.audit.record(
                request,
                "execution_error",
                "The authorized action raised an exception.",
            )
            raise

        self.audit.record(
            request,
            "executed",
            decision.reason,
        )

        return ExecutionResult(
            executed=True,
            decision=decision,
            output=output,
        )
