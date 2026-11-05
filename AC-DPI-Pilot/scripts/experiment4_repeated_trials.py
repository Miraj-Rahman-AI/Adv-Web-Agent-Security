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
        description="Experiment 4: Repeated-trial evaluation"
    )

    parser.add_argument(
        "--model",
        default=settings.default_model
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=settings.repetitions
    )

    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("Repetitions must be positive.")

    client = OllamaClient()

    pairs = []
    records = []

    print("=" * 65)
    print("AC-DPI-PILOT — EXPERIMENT 4")
    print("REPEATED-TRIAL ATTACK SUCCESS AND ROBUSTNESS")
    print("=" * 65)

    for scenario in SCENARIOS:

        for repetition in range(1, args.repetitions + 1):

            seed = settings.seed + repetition - 1

            print(
                f"\n{scenario['id']} | "
                f"Repetition {repetition}/{args.repetitions}"
            )

            baseline = run_trial(
                scenario=scenario,
                condition="BASELINE",
                model=args.model,
                client=client,
                seed=seed
            )

            attack = run_trial(
                scenario=scenario,
                condition="DIRECT_PROMPT_INJECTION",
                model=args.model,
                client=client,
                seed=seed
            )

            trajectory = compare_trajectories(
                baseline,
                attack
            )

            pair = {

                "scenario_id": scenario["id"],

                "repetition": repetition,

                "seed": seed,

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
                "Task-preserving success:",
                attack["metrics"]["task_preserving_attack_success"]
            )

    summary = {

        "model": args.model,

        "repetitions_per_scenario": args.repetitions,

        "total_paired_trials": len(pairs),

        "paired_summary": summarize_pairs(pairs),

        "scenario_results": [

            {
                "scenario_id": scenario["id"],

                "paired_trials": [
                    pair for pair in pairs
                    if pair["scenario_id"] == scenario["id"]
                ]

            }

            for scenario in SCENARIOS
        ]

    }

    artifacts = save_experiment(
        "experiment4_repeated_trials",
        summary,
        records
    )

    print("\nExperiment 4 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
