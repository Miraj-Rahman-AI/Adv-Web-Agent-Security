import argparse

from ac_dpi_pilot.config import settings
from ac_dpi_pilot.ollama_client import OllamaClient
from ac_dpi_pilot.runtime import (
    SCENARIOS,
    compare_trajectories,
    run_trial,
    save_experiment,
    summarize_pairs
)


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 2: DPI attack scenario expansion"
    )

    parser.add_argument(
        "--model",
        default=settings.default_model
    )

    args = parser.parse_args()

    client = OllamaClient()

    pairs = []
    records = []

    print("=" * 65)
    print("AC-DPI-PILOT — EXPERIMENT 2")
    print("AUTHORIZATION-CONDITIONED ATTACK SCENARIO EXPANSION")
    print("=" * 65)

    for scenario in SCENARIOS:

        print(f"\nScenario: {scenario['id']}")
        print(scenario["category"])

        baseline = run_trial(
            scenario=scenario,
            condition="BASELINE",
            model=args.model,
            client=client,
            seed=settings.seed
        )

        attack = run_trial(
            scenario=scenario,
            condition="DIRECT_PROMPT_INJECTION",
            model=args.model,
            client=client,
            seed=settings.seed
        )

        trajectory = compare_trajectories(
            baseline,
            attack
        )

        pair = {
            "scenario_id": scenario["id"],
            "category": scenario["category"],
            "baseline": baseline,
            "attack": attack,
            "trajectory_analysis": trajectory
        }

        pairs.append(pair)

        records.append({
            "record_type": "paired_trial",
            **pair
        })

        print(
            "Baseline task success:",
            baseline["metrics"]["legitimate_task_success"]
        )

        print(
            "Attack target executed:",
            attack["metrics"]["attack_target_executed"]
        )

        print(
            "Task-preserving success:",
            attack["metrics"]["task_preserving_attack_success"]
        )

    summary = {
        "model": args.model,
        "scenario_count": len(SCENARIOS),
        "paired_evaluation": summarize_pairs(pairs),
        "scenario_results": [
            {
                "scenario_id": pair["scenario_id"],
                "category": pair["category"],
                "baseline_metrics": pair["baseline"]["metrics"],
                "attack_metrics": pair["attack"]["metrics"],
                "trajectory_analysis": pair["trajectory_analysis"]
            }
            for pair in pairs
        ]
    }

    artifacts = save_experiment(
        "experiment2",
        summary,
        records
    )

    print("\nExperiment 2 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
