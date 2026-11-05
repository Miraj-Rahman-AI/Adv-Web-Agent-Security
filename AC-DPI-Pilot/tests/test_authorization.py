from ac_dpi_pilot.runtime import (
    SCENARIOS_BY_ID,
    is_authorized,
    is_attack_target,
    execute_action
)


def test_s1_authorized_action():

    scenario = SCENARIOS_BY_ID["S1"]

    assert is_authorized(
        "get_order_summary",
        {"order_id": "1025"},
        scenario
    )


def test_s1_unauthorized_action():

    scenario = SCENARIOS_BY_ID["S1"]

    assert not is_authorized(
        "get_customer_details",
        {"order_id": "1025"},
        scenario
    )


def test_s3_billing_profile_unauthorized():

    scenario = SCENARIOS_BY_ID["S3"]

    assert not is_authorized(
        "get_billing_profile",
        {"invoice_id": "INV-204"},
        scenario
    )


def test_s5_delivery_status_is_authorized():

    scenario = SCENARIOS_BY_ID["S5"]

    assert is_authorized(
        "get_delivery_status",
        {"order_id": "1025"},
        scenario
    )


def test_attack_target_identification():

    scenario = SCENARIOS_BY_ID["S1"]

    assert is_attack_target(
        "get_customer_details",
        {"order_id": "1025"},
        scenario
    )


def test_vulnerable_executor_records_unauthorized_execution():

    scenario = SCENARIOS_BY_ID["S1"]

    result = execute_action(
        "get_customer_details",
        {"order_id": "1025"},
        scenario,
        enforce_policy=False
    )

    assert result["authorized"] is False
    assert result["status"] == "executed"


def test_enforcement_extension_blocks_unauthorized_action():

    scenario = SCENARIOS_BY_ID["S1"]

    result = execute_action(
        "get_customer_details",
        {"order_id": "1025"},
        scenario,
        enforce_policy=True
    )

    assert result["authorized"] is False
    assert result["status"] == "blocked"
    assert result["result"] is None
