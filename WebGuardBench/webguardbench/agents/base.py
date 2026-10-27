from typing import Protocol

from ..scenarios.schema import Action, Scenario


class AgentAdapter(Protocol):
    """Agents propose; the runner exclusively owns action execution."""

    metadata: dict

    async def initialize(self, scenario: Scenario, seed: int) -> None: ...
    async def propose_action(self, observation: dict) -> Action | None: ...
    async def shutdown(self) -> None: ...
