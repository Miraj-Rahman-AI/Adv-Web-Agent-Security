import argparse

from collections import defaultdict

from ac_dpi_pilot.config import settings
from ac_dpi_pilot.ollama_client import OllamaClient

from ac_dpi_pilot.runtime import (
    SCENARIOS,
    PROMPT_VARIANTS,
    compare_trajectories,
    run_trial,
    save_experiment,
    summarize_pairs
)


TOOL_EXPOSURES = [
    "FULL",
    "TASK_SCOPED"
]


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 5: Cross-model generalization"
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=2
    )

    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("Repetitions must be positive.")

    client = OllamaClient()

    models = list(settings.models)

    pairs = []

    records = []

    expected_calls = (
        len(models)
        * len(TOOL_EXPOSURES)
        * len(SCENARIOS)
        * args.repetitions
        * (1 + len(PROMPT_VARIANTS))
    )

    print("=" * 70)
    print("EXPERIMENT 5 — CROSS-MODEL GENERALIZATION")
    print("=" * 70)

    print("Models:", models)
    print("Scenarios:", len(SCENARIOS))
    print("Prompt variants:", len(PROMPT_VARIANTS))
    print("Tool configurations:", TOOL_EXPOSURES)
    print("Repetitions:", args.repetitions)
    print("Expected model calls:", expected_calls)

    completed_calls = 0

    for model in models:

        for exposure in TOOL_EXPOSURES:

            for scenario in SCENARIOS:

                for repetition in range(1, args.repetitions + 1):

                    seed = settings.seed + repetition - 1

                    print(
                        f"\n{model} | {exposure} | "
                        f"{scenario['id']} | R{repetition}"
                    )

                    baseline = run_trial(
                        scenario=scenario,
                        condition="BASELINE",
                        model=model,
                        client=client,
                        tool_exposure=exposure,
                        seed=seed
                    )

                    completed_calls += 1

                    records.append({
                        "record_type": "trial",
                        "trial_type": "baseline",
                        "model": model,
                        "scenario_id": scenario["id"],
                        "repetition": repetition,
                        "trial": baseline
                    })

                    for variant in PROMPT_VARIANTS:

                        attack = run_trial(
                            scenario=scenario,
                            condition="DIRECT_PROMPT_INJECTION",
                            model=model,
                            client=client,
                            prompt_variant=variant,
                            tool_exposure=exposure,
                            seed=seed
                        )

                        completed_calls += 1

                        trajectory = compare_trajectories(
                            baseline,
                            attack
                        )

                        pair = {

                            "model": model,

                            "tool_exposure": exposure,

                            "scenario_id": scenario["id"],

                            "repetition": repetition,

                            "prompt_variant": variant,

                            "baseline": baseline,

                            "attack": attack,

                            "trajectory_analysis": trajectory

                        }

                        pairs.append(pair)

                        records.append({
                            "record_type": "paired_trial",
                            **pair
                        })

    grouped = defaultdict(list)

    for pair in pairs:

        key = (
            pair["model"],
            pair["tool_exposure"],
            pair["prompt_variant"]
        )

        grouped[key].append(pair)

    group_results = []

    for key, items in sorted(grouped.items()):

        group_results.append({

            "model": key[0],

            "tool_exposure": key[1],

            "prompt_variant": key[2],

            "summary": summarize_pairs(items)

        })

    summary = {

        "models": models,

        "scenarios": [item["id"] for item in SCENARIOS],

        "prompt_variants": list(PROMPT_VARIANTS),

        "tool_exposures": TOOL_EXPOSURES,

        "repetitions": args.repetitions,

        "expected_model_calls": expected_calls,

        "completed_model_calls": completed_calls,

        "group_results": group_results

    }

    artifacts = save_experiment(
        "experiment5_cross_model_generalization",
        summary,
        records
    )

    print("\nExperiment 5 completed.")
    print("Completed calls:", completed_calls)
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
