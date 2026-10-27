import json

import pytest

from webguardbench.scenarios.loader import load_scenario, load_scenarios
from webguardbench.scenarios.schema import Action, scenario_from_dict


def test_bundled_suite_is_paired_and_round_trips(tmp_path):
    scenarios = load_scenarios()
    assert len(scenarios) == 6
    assert sum(s.attack is not None for s in scenarios) == 3
    for scenario in scenarios:
        path = tmp_path / "scenario.json"
        path.write_text(json.dumps(scenario.to_dict()), encoding="utf-8")
        assert load_scenario(path) == scenario


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(version=True),
        lambda d: d.update(version=2),
        lambda d: d.update(scenario_id="../../escape"),
        lambda d: d.update(unrecognized=True),
        lambda d: d.update(recovery_window=0),
        lambda d: d["task"].update(permitted_actions=["read", "purchase"]),
        lambda d: d["task"].update(permitted_actions=["read", "read"]),
        lambda d: d["task"].update(prohibited_actions=[]),
        lambda d: d["task"].update(success_effect="agent_said_done"),
        lambda d: d["environment"].update(synthetic_data="true"),
        lambda d: d["environment"].update(type="production"),
        lambda d: d["attack"].update(objective_effect="claimed_purchase"),
        lambda d: d["script"][0].update(target="https://third-party.example"),
        lambda d: d.update(script=[]),
    ],
)
def test_rejects_inconsistent_or_unsafe_scenarios(shopping, mutate):
    data = shopping.to_dict()
    mutate(data)
    with pytest.raises(ValueError):
        scenario_from_dict(data)


@pytest.mark.parametrize(
    "content,suffix",
    [
        ("a: 1\na: 2\n", ".yaml"),
        ('{"a":1,"a":2}', ".json"),
        ("!!python/object/apply:os.system ['echo unexpected']", ".yaml"),
    ],
)
def test_loader_rejects_duplicate_keys_and_executable_yaml(tmp_path, content, suffix):
    import yaml

    path = tmp_path / ("bad" + suffix)
    path.write_text(content, encoding="utf-8")
    with pytest.raises((ValueError, yaml.YAMLError)):
        load_scenario(path)


def test_rejects_duplicate_ids_and_empty_suites(shopping, tmp_path):
    with pytest.raises(ValueError, match="No scenarios"):
        load_scenarios(tmp_path)
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps(shopping.to_dict()), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_scenarios(tmp_path)


@pytest.mark.parametrize(
    "action",
    [{"kind": "eval", "target": "code"}, {"kind": "read"}, {"kind": "report", "target": "x"}],
)
def test_invalid_actions_are_rejected(action):
    with pytest.raises(ValueError):
        Action.from_dict(action)
