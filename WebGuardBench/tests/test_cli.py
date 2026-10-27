import csv
import json

import pytest

from webguardbench.cli import main


def test_end_to_end_cli_artifacts_and_re_evaluation(tmp_path):
    output = tmp_path / "experiment"
    assert main(["run", "--output", str(output), "--seed", "42"]) == 0
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert len(report["trials"]) == 12
    assert len(report["runtime_pairs"]) == 6
    assert report["groups"]["none"]["attack_success_rate"]["value"] == 1
    assert report["groups"]["allowlist"]["attack_success_rate"]["value"] == 0
    assert all(r["agent"]["scripted_fixture"] for r in report["trials"])
    assert len(list(csv.DictReader((output / "trials.csv").open(encoding="utf-8")))) == 12
    trial = next((output / "trials").iterdir())
    metrics = tmp_path / "evaluated.json"
    assert (
        main(
            [
                "evaluate",
                "--scenario",
                str(trial / "scenario.json"),
                "--trajectory",
                str(trial / "trajectory.json"),
                "--output",
                str(metrics),
            ]
        )
        == 0
    )
    assert json.loads(metrics.read_text()) == json.loads((trial / "metrics.json").read_text())
    assert main(["run", "--output", str(output)]) == 2
    assert (
        main(
            [
                "evaluate",
                "--scenario",
                str(trial / "scenario.json"),
                "--trajectory",
                str(trial / "trajectory.json"),
                "--output",
                str(metrics),
            ]
        )
        == 2
    )


@pytest.mark.parametrize(
    "args",
    [
        ["--trials", "0"],
        ["--seed", "-1"],
        ["--max-steps", "0"],
        ["--timeout", "nan"],
        ["--defenses", "none,none"],
        ["--defenses", "unknown"],
    ],
)
def test_invalid_cli_options_do_not_create_results(tmp_path, args):
    output = tmp_path / "results"
    assert main(["run", "--output", str(output), *args]) == 2
    assert not output.exists()


def test_config_relative_scenario_paths_and_override(shopping, tmp_path):
    (tmp_path / "scenario.json").write_text(json.dumps(shopping.to_dict()), encoding="utf-8")
    config = tmp_path / "experiment.yaml"
    config.write_text(
        "scenario: scenario.json\ntrials: 2\ndefenses:\n  - name: none\n", encoding="utf-8"
    )
    output = tmp_path / "results"
    assert main(["run", "--config", str(config), "--trials", "1", "--output", str(output)]) == 0
    report = json.loads((output / "report.json").read_text())
    assert len(report["trials"]) == 1


def test_incomplete_runs_have_nonzero_exit_and_reports(tmp_path):
    output = tmp_path / "results"
    assert main(["run", "--max-steps", "1", "--output", str(output)]) == 1
    report = json.loads((output / "report.json").read_text())
    assert report["groups"]["none"]["eligible_trials"] == 0
    assert report["groups"]["none"]["attack_success_rate"]["value"] is None


def test_validate_command():
    assert main(["validate"]) == 0
