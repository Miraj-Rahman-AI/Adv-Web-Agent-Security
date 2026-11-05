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
        description="Optional authorization-enforcement experiment"
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

            # Baseline: normal execution.

            baseline = run_trial(
                scenario=scenario,
                condition="BASELINE",
                model=args.model,
                client=client,
                seed=seed,
                enforce_policy=False
            )

            # Attack: vulnerable execution.

            vulnerable = run_trial(
                scenario=scenario,
                condition="DIRECT_PROMPT_INJECTION",
                model=args.model,
                client=client,
                seed=seed,
                enforce_policy=False
            )

            # Attack: authorization enforcement enabled.

            enforced = run_trial(
                scenario=scenario,
                condition="DIRECT_PROMPT_INJECTION",
                model=args.model,
                client=client,
                seed=seed,
                enforce_policy=True
            )

            pair = {

                "scenario_id": scenario["id"],

                "repetition": repetition,

                "baseline": baseline,

                "vulnerable_attack": vulnerable,

                "enforced_attack": enforced,

                "vulnerable_trajectory": compare_trajectories(
                    baseline,
                    vulnerable
                ),

                "enforced_trajectory": compare_trajectories(
                    baseline,
                    enforced
                )

            }

            pairs.append(pair)

            records.append({
                "record_type": "enforcement_comparison",
                **pair
            })

            print(
                scenario["id"],
                "Vulnerable target execution:",
                vulnerable["metrics"]["attack_target_executed"],
                "Enforced target execution:",
                enforced["metrics"]["attack_target_executed"]
            )

    vulnerable_pairs = [
        {
            "baseline": item["baseline"],
            "attack": item["vulnerable_attack"]
        }
        for item in pairs
    ]

    enforced_pairs = [
        {
            "baseline": item["baseline"],
            "attack": item["enforced_attack"]
        }
        for item in pairs
    ]

    summary = {

        "experiment": (
            "Experiment 5.3 v2 - Authorization Enforcement Extension"
        ),

        "research_scope": "Optional defensive extension",

        "vulnerable_execution": summarize_pairs(
            vulnerable_pairs
        ),

        "authorization_enforced_execution": summarize_pairs(
            enforced_pairs
        ),

        "scenario_count": len(SCENARIOS),

        "repetitions": args.repetitions

    }

    artifacts = save_experiment(
        "experiment5_3_authorization_enforcement_v2",
        summary,
        records
    )

    print("\nAuthorization-enforcement extension completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
