from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from ..scenarios.schema import Action


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class Step:
    index: int
    action: Action
    authorized: bool
    defense_allowed: bool | None = None
    defense_reason: str | None = None
    outcome_known: bool = False
    executed: bool = False
    success: bool = False
    effects: list[str] = field(default_factory=list)
    defense_seconds: float = 0.0
    elapsed_seconds: float = 0.0
    observation_before: dict = field(default_factory=dict)
    observation_after: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class Trajectory:
    scenario_id: str
    seed: int
    agent: dict
    defense: dict
    backend: str
    environment: dict = field(default_factory=dict)
    trial_id: str = field(default_factory=lambda: uuid4().hex)
    started_utc: str = field(default_factory=utc_now)
    status: str = "running"
    steps: list[Step] = field(default_factory=list)
    final_observation: dict = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
