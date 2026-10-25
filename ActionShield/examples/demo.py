import asyncio

from actionshield import (
    ActionImpact,
    ActionPolicy,
    ActionRequest,
    ActionShield,
    ActionType,
)
from actionshield.audit import JsonlAuditLogger


async def main():
    policy = ActionPolicy(
        policy_id="demo-policy",
        allowed_domains=frozenset({
            "example.com",
        }),
        allow_subdomains=False,
    )

    audit = JsonlAuditLogger(
        "logs/actionshield-audit.jsonl"
    )

    shield = ActionShield(
        policy=policy,
        audit=audit,
    )

    request = ActionRequest(
        action_type=ActionType.SUBMIT,
        current_url="https://example.com/checkout",
        description="Submit a checkout form",
        target="button#confirm",
        impact=ActionImpact.HIGH,
    )

    async def request_approval(action, decision):
        print("Action requires approval.")
        print("Action:", action.action_type.value)
        print("Reason:", decision.reason)

        answer = input(
            "Approve this simulated action? Type YES: "
        )

        return answer.strip() == "YES"

    async def simulated_browser_action():
        print("Authorized callback executed.")
        return {"status": "simulated"}

    result = await shield.execute(
        request=request,
        action=simulated_browser_action,
        approval_callback=request_approval,
    )

    print("Executed:", result.executed)
    print("Decision:", result.decision.status.value)
    print("Reason:", result.decision.reason)


if __name__ == "__main__":
    asyncio.run(main())
