from ac_dpi_pilot.runtime import (
    SCENARIOS_BY_ID,
    TOOL_HANDLERS,
    build_tool_catalog,
    execute_action
)


def main():

    print("=" * 55)
    print("AVAILABLE WEB AGENT TOOLS")
    print("=" * 55)

    for index, name in enumerate(
        TOOL_HANDLERS,
        start=1
    ):

        print(f"{index}. {name}")

    print("\nFull tool catalog:")

    print(build_tool_catalog("FULL"))

    print("\nExecuting an example tool call:")

    scenario = SCENARIOS_BY_ID["S1"]

    result = execute_action(
        "get_order_summary",
        {"order_id": "1025"},
        scenario
    )

    print(result)


if __name__ == "__main__":
    main()
