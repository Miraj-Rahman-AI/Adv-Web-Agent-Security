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
        description="Experiment 5.1: Cross-model replication"
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

    for model in settings.models:

        for scenario in SCENARIOS:

            for repetition in range(1, args.repetitions + 1):

                seed = settings.seed + repetition - 1

                baseline = run_trial(
                    scenario=scenario,
                    condition="BASELINE",
                    model=model,
                    client=client,
                    seed=seed
                )

                attack = run_trial(
                    scenario=scenario,
                    condition="DIRECT_PROMPT_INJECTION",
                    model=model,
                    client=client,
                    prompt_variant="TASK_PRESERVING_ADDITIVE",
                    seed=seed
                )

                pair = {

                    "model": model,

                    "scenario_id": scenario["id"],

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
                    model,
                    scenario["id"],
                    repetition,
                    attack["metrics"]["task_preserving_attack_success"]
                )

    model_results = []

    for model in settings.models:

        model_pairs = [
            pair for pair in pairs
            if pair["model"] == model
        ]

        model_results.append({

            "model": model,

            "summary": summarize_pairs(model_pairs)

        })

    summary = {

        "repetitions": args.repetitions,

        "prompt_variant": "TASK_PRESERVING_ADDITIVE",

        "model_results": model_results

    }

    artifacts = save_experiment(
        "experiment5_1_cross_model_replication",
        summary,
        records
    )

    print("\nExperiment 5.1 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
