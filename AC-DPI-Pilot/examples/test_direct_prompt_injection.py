import argparse
import json

from ac_dpi_pilot.config import settings
from ac_dpi_pilot.ollama_client import OllamaClient

from ac_dpi_pilot.runtime import (
    SCENARIOS_BY_ID,
    build_attack_message,
    build_system_prompt,
    run_trial
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        default="S1",
        choices=["S1", "S2", "S3", "S4", "S5"]
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Actually execute the model experiment."
    )

    args = parser.parse_args()

    scenario = SCENARIOS_BY_ID[args.scenario]

    system_prompt = build_system_prompt(scenario)

    attack_message = build_attack_message(
        scenario,
        variant="TASK_PRESERVING_ADDITIVE"
    )

    print("=" * 65)
    print("DIRECT PROMPT INJECTION EXAMPLE")
    print("=" * 65)

    print("\nSYSTEM PROMPT:")

    print(system_prompt)

    print("\nATTACK MESSAGE:")

    print(attack_message)

    if not args.run:

        print(
            "\nPrompt preview completed. "
            "No model request was performed."
        )

        return

    client = OllamaClient()

    result = run_trial(
        scenario=scenario,
        condition="DIRECT_PROMPT_INJECTION",
        model=settings.default_model,
        client=client
    )

    print("\nMODEL RESULT:")

    print(
        json.dumps(
            {
                "plan": result["plan"],
                "metrics": result["metrics"],
                "events": result["events"],
                "error": result["error"]
            },
            indent=4
        )
    )


if __name__ == "__main__":
    main()
