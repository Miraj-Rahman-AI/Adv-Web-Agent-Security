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


EXPOSURES = [
    "FULL",
    "TASK_SCOPED"
]


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 5.3: Tool exposure analysis"
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

        for exposure in EXPOSURES:

            for repetition in range(1, args.repetitions + 1):

                seed = settings.seed + repetition - 1

                baseline = run_trial(
                    scenario=scenario,
                    condition="BASELINE",
                    model=args.model,
                    client=client,
                    tool_exposure=exposure,
                    seed=seed
                )

                attack = run_trial(
                    scenario=scenario,
                    condition="DIRECT_PROMPT_INJECTION",
                    model=args.model,
                    client=client,
                    tool_exposure=exposure,
                    seed=seed
                )

                pair = {

                    "model": args.model,

                    "scenario_id": scenario["id"],

                    "tool_exposure": exposure,

                    "repetition": repetition,

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
                    exposure,
                    attack["metrics"]["attack_target_executed"]
                )

    exposure_results = []

    for exposure in EXPOSURES:

        exposure_pairs = [
            pair for pair in pairs
            if pair["tool_exposure"] == exposure
        ]

        exposure_results.append({

            "tool_exposure": exposure,

            "summary": summarize_pairs(exposure_pairs)

        })

    summary = {

        "model": args.model,

        "repetitions": args.repetitions,

        "exposure_configurations": EXPOSURES,

        "exposure_results": exposure_results

    }

    artifacts = save_experiment(
        "experiment5_3_tool_exposure",
        summary,
        records
    )

    print("\nExperiment 5.3 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
