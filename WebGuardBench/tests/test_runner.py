import asyncio
import importlib.util

import pytest

from webguardbench.agents.adapters import ScriptedAgent
from webguardbench.defenses import Defense
from webguardbench.environments.synthetic import InMemoryEnvironment
from webguardbench.evaluator import evaluate_trajectory
from webguardbench.runner.experiment import run_experiment
from webguardbench.scenarios.loader import load_scenarios
from webguardbench.scenarios.schema import Action


@pytest.mark.parametrize("scenario", load_scenarios(), ids=lambda s: s.scenario_id)
@pytest.mark.parametrize("defense", ["none", "allowlist"])
def test_all_fixtures_complete_with_expected_effects(scenario, defense):
    raw = asyncio.run(run_experiment(scenario, defense=Defense(defense), seed=123))
    result = evaluate_trajectory(scenario, raw)
    assert raw.status == "completed"
    assert result["task_success"] is True
    if scenario.attack:
        assert result["attack_success"] == (defense == "none")


def test_seeded_runs_have_identical_behavior(shopping):
    a = asyncio.run(run_experiment(shopping, seed=42))
    b = asyncio.run(run_experiment(shopping, seed=42))
    assert a.trial_id != b.trial_id
    assert [s.action for s in a.steps] == [s.action for s in b.steps]
    assert a.final_observation == b.final_observation


def test_timeout_preserves_partial_proposals_and_closes_resources(shopping):
    class SlowEnvironment(InMemoryEnvironment):
        closed = False

        async def execute(self, action):
            await asyncio.sleep(10)

        async def close(self):
            self.closed = True

    env = SlowEnvironment()
    result = asyncio.run(run_experiment(shopping, environment=env, timeout_seconds=0.02))
    assert env.closed
    assert result.status == "timeout"
    assert len(result.steps) == 1
    assert not result.steps[0].executed
    assert evaluate_trajectory(shopping, result)["eligible"] is False


def test_invalid_target_is_recorded_as_error_and_not_executed(shopping):
    class BadAgent(ScriptedAgent):
        async def propose_action(self, observation):
            return Action("read", "../../outside")

    raw = asyncio.run(run_experiment(shopping, agent=BadAgent()))
    assert raw.status == "error"
    assert not raw.steps[0].executed
    assert evaluate_trajectory(shopping, raw)["eligible"] is False


def test_agent_cannot_mutate_recorded_evidence(shopping):
    class MutatingAgent(ScriptedAgent):
        async def propose_action(self, observation):
            observation["effects"].append("purchase_completed")
            return None

    raw = asyncio.run(run_experiment(shopping, agent=MutatingAgent()))
    assert raw.final_observation["effects"] == []
    assert evaluate_trajectory(shopping, raw)["attack_success"] is False


def test_observation_failure_preserves_confirmed_attack_effect(shopping):
    class FailingObserver(InMemoryEnvironment):
        async def observe(self):
            if "purchase_completed" in self.state.effects:
                raise RuntimeError("Synthetic observation failure")
            return await super().observe()

    raw = asyncio.run(run_experiment(shopping, environment=FailingObserver()))
    assert raw.status == "error"
    assert raw.steps[1].outcome_known
    assert raw.steps[1].effects == ["purchase_completed"]
    assert evaluate_trajectory(shopping, raw)["attack_success"] is True


@pytest.mark.skipif(
    importlib.util.find_spec("actionshield") is None,
    reason="Set PYTHONPATH to the repository's ActionShield directory",
)
def test_real_actionshield_integration_blocks_purchase(shopping):
    raw = asyncio.run(run_experiment(shopping, defense=Defense("actionshield")))
    result = evaluate_trajectory(shopping, raw)
    assert result["eligible"] and result["task_success"]
    assert result["attack_success"] is False
    assert raw.steps[1].defense_reason.startswith("Action 'purchase'")
