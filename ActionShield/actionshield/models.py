from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SUBMIT = "submit"
    DOWNLOAD = "download"
    PURCHASE = "purchase"
    DELETE = "delete"
    SEND = "send"
    MODIFY = "modify"


class ActionImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """A structured description of a proposed browser action."""

    action_type: ActionType
    current_url: str | None = None
    destination_url: str | None = None
    description: str = ""
    target: str | None = None
    impact: ActionImpact = ActionImpact.LOW
    request_id: str = field(
        default_factory=lambda: uuid4().hex
    )


@dataclass(frozen=True, slots=True)
class ActionDecision:
    """The security engine's authorization decision."""

    status: DecisionStatus
    reason: str
    policy_id: str


@dataclass(slots=True)
class ExecutionResult:
    """Result of a guarded execution attempt."""

    executed: bool
    decision: ActionDecision
    output: Any = None
