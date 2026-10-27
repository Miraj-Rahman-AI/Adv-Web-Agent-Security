from dataclasses import dataclass

from .scenarios.schema import ACTIONS, Action


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


class Defense:
    def __init__(self, name="none", allowed_actions=None):
        if not isinstance(name, str) or name not in {"none", "allowlist", "actionshield"}:
            raise ValueError(f"Unknown defense: {name}")
        if allowed_actions is None:
            allowed_actions = ["read", "compare", "report"]
        if not isinstance(allowed_actions, list) or not all(
            isinstance(a, str) for a in allowed_actions
        ):
            raise ValueError("Defense allowed_actions must be a list")
        if set(allowed_actions) - ACTIONS or len(allowed_actions) != len(set(allowed_actions)):
            raise ValueError("Defense allowed_actions contains unknown or duplicate actions")
        self.name = name
        self.allowed_actions = frozenset(allowed_actions)
        self.metadata = {"name": name, "allowed_actions": sorted(self.allowed_actions)}
        if name == "actionshield":
            try:
                from actionshield import ActionPolicy, ActionShield, ActionType
            except ImportError as exc:
                raise RuntimeError(
                    "Add the repository's ActionShield directory to PYTHONPATH; "
                    "see README Agent and defense integration"
                ) from exc
            self.action_types = {
                "read": ActionType.NAVIGATE,
                "compare": ActionType.CLICK,
                "report": ActionType.CLICK,
                "purchase": ActionType.PURCHASE,
                "send": ActionType.SEND,
                "delete": ActionType.DELETE,
            }
            self.engine = ActionShield(
                ActionPolicy(
                    policy_id="webguardbench-local",
                    allowed_domains=frozenset({"127.0.0.1"}),
                    allowed_actions=frozenset(self.action_types[a] for a in self.allowed_actions),
                    require_approval_for=frozenset(),
                    require_approval_for_impact=frozenset(),
                )
            )

    async def decide(self, action: Action, url: str) -> Decision:
        if self.name == "none":
            return Decision(True, "No additional defense")
        if self.name == "allowlist":
            allowed = action.kind in self.allowed_actions
            return Decision(allowed, "Allowed by action list" if allowed else "Not in action list")
        from actionshield import ActionRequest, DecisionStatus

        request = ActionRequest(
            action_type=self.action_types[action.kind],
            current_url=url,
            destination_url=url if action.kind == "read" else None,
            target=action.target,
        )
        result = self.engine.evaluate(request)
        return Decision(result.status == DecisionStatus.ALLOW, result.reason)
