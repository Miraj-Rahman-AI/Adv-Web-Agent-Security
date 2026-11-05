import json

from ac_dpi_pilot.runtime import (
    SCENARIOS_BY_ID,
    execute_action
)


def main():

    scenario = SCENARIOS_BY_ID["S1"]

    result = execute_action(
        action="get_order_summary",
        arguments={"order_id": "1025"},
        scenario=scenario
    )

    print("Action execution result:")

    print(
        json.dumps(
            result,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
