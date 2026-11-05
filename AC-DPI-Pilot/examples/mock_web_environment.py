import argparse
import json

from ac_dpi_pilot.runtime import (
    SCENARIOS_BY_ID,
    execute_action
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--enforce-policy",
        action="store_true"
    )

    args = parser.parse_args()

    scenario = SCENARIOS_BY_ID["S1"]

    print("=" * 55)
    print("AC-DPI-PILOT MOCK WEB ENVIRONMENT")
    print("=" * 55)

    print("\n1. Authorized action")

    authorized_result = execute_action(
        "get_order_summary",
        {"order_id": "1025"},
        scenario,
        enforce_policy=args.enforce_policy
    )

    print(
        json.dumps(
            authorized_result,
            indent=4
        )
    )

    print("\n2. Unauthorized action")

    unauthorized_result = execute_action(
        "get_customer_details",
        {"order_id": "1025"},
        scenario,
        enforce_policy=args.enforce_policy
    )

    print(
        json.dumps(
            unauthorized_result,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
