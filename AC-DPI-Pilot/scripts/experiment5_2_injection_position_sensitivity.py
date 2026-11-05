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


POSITIONS = [
    "PREFIX",
    "INTERLEAVED",
    "SUFFIX"
]


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 5.2: Injection-position sensitivity"
    )

    parser.add_argument(
        "--model",
        default=settings.default_model
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=5
    )

    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("Repetitions must be positive.")

    client = OllamaClient()

    pairs = []
    records = []

    for scenario in SCENARIOS:

        for repetition in range(1, args.repetitions + 1):

            seed = settings.seed + repetition - 1

            baseline = run_trial(
                scenario=scenario,
                condition="BASELINE",
                model=args.model,
                client=client,
                seed=seed
            )

            for position in POSITIONS:

                attack = run_trial(
                    scenario=scenario,
                    condition="DIRECT_PROMPT_INJECTION",
                    model=args.model,
                    client=client,
                    position=position,
                    seed=seed
                )

                pair = {

                    "model": args.model,

                    "scenario_id": scenario["id"],

                    "repetition": repetition,

                    "position": position,

                    "baseline": baseline,

                    "attack": attack,

                    "trajectory_analysis": compare_trajectories(
                        baseline,
                        attack
                    )

                }

                pairs.append(pair)

                records.append({
                    "record_type": "paired_trial",
                    **pair
                })

                print(
                    scenario["id"],
                    position,
                    attack["metrics"]["task_preserving_attack_success"]
                )

    position_results = []

    for position in POSITIONS:

        position_pairs = [
            pair for pair in pairs
            if pair["position"] == position
        ]

        position_results.append({

            "position": position,

            "summary": summarize_pairs(position_pairs)

        })

    summary = {

        "model": args.model,

        "positions": POSITIONS,

        "repetitions": args.repetitions,

        "position_results": position_results

    }

    artifacts = save_experiment(
        "experiment5_2_injection_position_sensitivity",
        summary,
        records
    )

    print("\nExperiment 5.2 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
