import asyncio
import copy
from dataclasses import asdict
from time import perf_counter

from ..agents.adapters import create_agent
from ..defenses import Defense
from ..environments.synthetic import InMemoryEnvironment
from ..scenarios.schema import Action, Scenario, integer
from .trajectory import Step, Trajectory


async def run_experiment(
    scenario: Scenario,
    agent_name="scripted",
    defense=None,
    *,
    backend="memory",
    seed=0,
    max_steps=50,
    timeout_seconds=60.0,
    agent=None,
    environment=None,
) -> Trajectory:
    integer(max_steps, "max_steps", 1, 10000)
    integer(seed, "seed", 0, 2**32 - 1)
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not 0 < timeout_seconds <= 86400
    ):
        raise ValueError("timeout_seconds must be in (0, 86400]")
    if backend not in {"memory", "browser"}:
        raise ValueError("backend must be memory or browser")
    defense = defense or Defense()
    trajectory = Trajectory(scenario.scenario_id, seed, {}, defense.metadata, backend)
    started = perf_counter()
    active_step = None
    try:
        async with asyncio.timeout(timeout_seconds):
            if agent is None:
                agent = create_agent(agent_name)
            trajectory.agent = dict(getattr(agent, "metadata", {"name": agent_name}))
            if environment is None:
                if backend == "browser":
                    from ..environments.browser import BrowserEnvironment

                    environment = BrowserEnvironment()
                else:
                    environment = InMemoryEnvironment()
            await environment.start(scenario)
            trajectory.environment = dict(getattr(environment, "metadata", {}))
            await agent.initialize(scenario, seed)
            observation = await environment.observe()
            trajectory.final_observation = observation
            previous = None
            for index in range(1, max_steps + 1):
                # The original observation is copied; an adapter cannot mutate the evidence.
                action = await agent.propose_action(
                    copy.deepcopy({**observation, "previous_result": previous})
                )
                if action is None:
                    trajectory.status = "completed"
                    break
                if not isinstance(action, Action):
                    raise ValueError("Agent must propose an Action or None")
                action = Action.from_dict(asdict(action))
                # Record proposal before defense/execution, including failed dispatches.
                active_step = Step(
                    index,
                    action,
                    scenario.authorized(action),
                    observation_before=copy.deepcopy(observation),
                )
                trajectory.steps.append(active_step)
                step_started = perf_counter()
                decision_started = perf_counter()
                decision = await defense.decide(action, environment.url)
                active_step.defense_seconds = perf_counter() - decision_started
                active_step.defense_allowed = decision.allowed
                active_step.defense_reason = decision.reason
                if decision.allowed:
                    outcome = await environment.execute(action)
                    active_step.executed = outcome.executed
                    active_step.success = outcome.success
                    active_step.effects = list(outcome.effects)
                    active_step.error = outcome.error
                active_step.outcome_known = True
                observation = await environment.observe()
                active_step.observation_after = copy.deepcopy(observation)
                trajectory.final_observation = copy.deepcopy(observation)
                active_step.elapsed_seconds = perf_counter() - step_started
                previous = {
                    "action": asdict(action),
                    "blocked": not decision.allowed,
                    "executed": active_step.executed,
                    "success": active_step.success,
                    "error": active_step.error,
                }
                active_step = None
            else:
                trajectory.status = "step_limit"
    except TimeoutError:
        trajectory.status = "timeout"
        trajectory.error = "Trial exceeded its configured time limit"
        if active_step:
            active_step.error = "Action outcome is incomplete after timeout"
    except Exception as exc:
        trajectory.status = "error"
        # Configured endpoints/custom adapters may carry secrets in error messages.
        trajectory.error = (
            f"{type(exc).__name__}: trial failed; inspect adapter/environment locally"
        )
        if active_step:
            active_step.error = trajectory.error
    finally:
        for resource in (agent, environment):
            if resource is None:
                continue
            try:
                async with asyncio.timeout(10):
                    if resource is agent:
                        await resource.shutdown()
                    else:
                        await resource.close()
            except Exception as exc:
                trajectory.status = "error"
                trajectory.error = f"{type(exc).__name__}: resource cleanup failed"
        trajectory.elapsed_seconds = perf_counter() - started
    return trajectory
