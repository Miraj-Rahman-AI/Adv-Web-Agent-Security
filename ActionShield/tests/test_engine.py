import asyncio

from actionshield import (
    ActionPolicy,
    ActionRequest,
    ActionShield,
    ActionType,
    DecisionStatus,
)
from actionshield.audit import InMemoryAuditLogger


def make_shield(allow_subdomains=False):
    policy = ActionPolicy(
        policy_id="test-policy",
        allowed_domains=frozenset({
            "example.com",
        }),
        allow_subdomains=allow_subdomains,
    )

    audit = InMemoryAuditLogger()

    return ActionShield(policy, audit), audit


def test_blocks_unlisted_domain():
    async def scenario():
        shield, audit = make_shield()
        called = False

        async def operation():
            nonlocal called
            called = True

        request = ActionRequest(
            action_type=ActionType.NAVIGATE,
            destination_url="https://evil.test/",
        )

        result = await shield.execute(
            request,
            operation,
        )

        assert not result.executed
        assert not called
        assert result.decision.status == DecisionStatus.DENY
        assert audit.events[-1]["status"] == "blocked"

    asyncio.run(scenario())


def test_blocks_subdomain_by_default():
    async def scenario():
        shield, _ = make_shield()

        request = ActionRequest(
            action_type=ActionType.NAVIGATE,
            destination_url="https://shop.example.com/",
        )

        decision = shield.evaluate(request)

        assert decision.status == DecisionStatus.DENY

    asyncio.run(scenario())


def test_allows_authorized_navigation():
    async def scenario():
        shield, _ = make_shield()

        request = ActionRequest(
            action_type=ActionType.NAVIGATE,
            destination_url="https://example.com/products",
        )

        decision = shield.evaluate(request)

        assert decision.status == DecisionStatus.ALLOW

    asyncio.run(scenario())


def test_submit_requires_approval():
    async def scenario():
        shield, _ = make_shield()
        called = False

        async def operation():
            nonlocal called
            called = True

        request = ActionRequest(
            action_type=ActionType.SUBMIT,
            current_url="https://example.com/checkout",
        )

        result = await shield.execute(
            request,
            operation,
            approval_callback=lambda request, decision: False,
        )

        assert not result.executed
        assert not called
        assert result.decision.status == DecisionStatus.DENY

    asyncio.run(scenario())


def test_approved_submit_executes():
    async def scenario():
        shield, audit = make_shield()
        called = False

        async def operation():
            nonlocal called
            called = True
            return "success"

        request = ActionRequest(
            action_type=ActionType.SUBMIT,
            current_url="https://example.com/checkout",
        )

        result = await shield.execute(
            request,
            operation,
            approval_callback=lambda request, decision: True,
        )

        assert result.executed
        assert called
        assert result.output == "success"
        assert result.decision.status == DecisionStatus.ALLOW
        assert audit.events[-1]["status"] == "executed"

    asyncio.run(scenario())


def test_invalid_url_is_denied():
    async def scenario():
        shield, _ = make_shield()

        request = ActionRequest(
            action_type=ActionType.NAVIGATE,
            destination_url="file:///etc/passwd",
        )

        decision = shield.evaluate(request)

        assert decision.status == DecisionStatus.DENY

    asyncio.run(scenario())
