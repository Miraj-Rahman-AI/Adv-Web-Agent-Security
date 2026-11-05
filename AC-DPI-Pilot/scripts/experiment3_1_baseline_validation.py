import argparse

from ac_dpi_pilot.config import settings
from ac_dpi_pilot.ollama_client import OllamaClient

from ac_dpi_pilot.runtime import (
    SCENARIOS,
    is_authorized,
    run_trial,
    save_experiment
)


def audit_scenario_policy(scenario):

    required_checks = []

    for required in scenario["required_calls"]:

        authorized = is_authorized(
            required["action"],
            required["arguments"],
            scenario
        )

        required_checks.append({

            "action": required["action"],

            "arguments": required["arguments"],

            "authorized": authorized

        })

    return {

        "scenario_id": scenario["id"],

        "required_calls": required_checks,

        "policy_consistent": all(
            item["authorized"]
            for item in required_checks
        )

    }


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 3.1: Baseline authorization validation"
    )

    parser.add_argument(
        "--model",
        default=settings.default_model
    )

    args = parser.parse_args()

    client = OllamaClient()

    results = []

    for scenario in SCENARIOS:

        print(f"\nValidating {scenario['id']}")

        policy_audit = audit_scenario_policy(scenario)

        baseline = run_trial(
            scenario=scenario,
            condition="BASELINE",
            model=args.model,
            client=client,
            seed=settings.seed
        )

        metrics = baseline["metrics"]

        result = {

            "scenario_id": scenario["id"],

            "category": scenario["category"],

            "policy_audit": policy_audit,

            "baseline": baseline,

            "baseline_task_success": (
                metrics["legitimate_task_success"]
            ),

            "baseline_unauthorized_execution": (
                metrics["unauthorized_action_executed"]
            ),

            "baseline_valid": (
                policy_audit["policy_consistent"]
                and baseline["model_call_status"] == "ok"
                and not metrics["unauthorized_action_executed"]
            )

        }

        results.append(result)

        print("Policy consistent:", policy_audit["policy_consistent"])

        print("Task success:", metrics["legitimate_task_success"])

        print(
            "Unauthorized execution:",
            metrics["unauthorized_action_executed"]
        )

    summary = {

        "model": args.model,

        "scenario_count": len(results),

        "policy_consistent_scenarios": sum(
            item["policy_audit"]["policy_consistent"]
            for item in results
        ),

        "baseline_valid_scenarios": sum(
            item["baseline_valid"]
            for item in results
        ),

        "results": results

    }

    artifacts = save_experiment(
        "experiment3_1_baseline_validation",
        summary,
        results
    )

    print("\nExperiment 3.1 completed.")
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
