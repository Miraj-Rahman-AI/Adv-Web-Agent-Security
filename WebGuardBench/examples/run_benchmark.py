"""Run the packaged shopping fixture through the public Python API."""

import asyncio
from pathlib import Path
from uuid import uuid4

from webguardbench.defenses import Defense
from webguardbench.evaluator import evaluate_trajectory
from webguardbench.reporting.reports import save_json, save_reports
from webguardbench.runner.experiment import run_experiment
from webguardbench.scenarios.loader import load_scenarios


async def main():
    scenario = next(s for s in load_scenarios() if s.scenario_id == "shopping_injection_001")
    experiment_id = uuid4().hex
    output = Path("results") / experiment_id
    results = []
    for name in ("none", "allowlist"):
        trajectory = await run_experiment(scenario, defense=Defense(name), seed=42)
        results.append(evaluate_trajectory(scenario, trajectory))
        trial = output / "trials" / trajectory.trial_id
        save_json(scenario.to_dict(), trial / "scenario.json")
        save_json(trajectory.to_dict(), trial / "trajectory.json")
        save_json(results[-1], trial / "metrics.json")
    info = {"experiment_id": experiment_id, "example": "Python API; scripted fixtures only"}
    save_json(info, output / "config.json")
    save_reports(results, output, info)
    print(output.resolve())


if __name__ == "__main__":
    asyncio.run(main())
