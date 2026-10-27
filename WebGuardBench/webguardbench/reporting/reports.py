import csv
import json
from pathlib import Path

from ..evaluator.security_metrics import aggregate_metrics, compare_defenses


def save_json(value, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )


def _cell(value):
    # Prevent formulas in spreadsheet software when custom adapter metadata is exported.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def save_reports(results: list[dict], output: str | Path, metadata: dict) -> dict:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    groups = {}
    for defense in sorted({r["defense"]["name"] for r in results}):
        groups[defense] = aggregate_metrics([r for r in results if r["defense"]["name"] == defense])
    report = {
        "metadata": metadata,
        "groups": groups,
        "trials": results,
        "runtime_pairs": compare_defenses(results),
    }
    save_json(report, output / "report.json")
    columns = [
        "trial_id",
        "scenario_id",
        "seed",
        "backend",
        "status",
        "eligible",
        "is_attack",
        "task_success",
        "attack_success",
        "goal_deviation",
        "first_deviation_step",
        "first_unauthorized_action_step",
        "proposed_actions",
        "executed_actions",
        "unauthorized_attempts",
        "unauthorized_executed",
        "authorized_proposals",
        "false_blocks",
        "deviation_episodes",
        "recovered_episodes",
        "elapsed_seconds",
        "defense_seconds",
        "error",
    ]
    with (output / "trials.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["agent", "defense", *columns])
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "agent": _cell(result["agent"].get("name", "unknown")),
                    "defense": _cell(result["defense"]["name"]),
                    **{key: _cell(result.get(key)) for key in columns},
                }
            )
    lines = [
        "# WebGuardBench experiment",
        "",
        f"Experiment: `{metadata['experiment_id']}`",
        "",
        "Scripted fixtures are software checks, not evidence of LLM security effectiveness.",
        "Incomplete trials are counted and excluded from all rate denominators.",
        "",
        "| Defense | Complete / total | ASR | UAR | Benign task success | False blocking |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, group in groups.items():

        def rate(key, group=group):
            value = group[key]
            return (
                f"{value['value']:.1%} ({value['numerator']}/{value['denominator']})"
                if value["value"] is not None
                else "n/a (0/0)"
            )

        lines.append(
            f"| {name} | {group['eligible_trials']} / {group['total_trials']} | "
            f"{rate('attack_success_rate')} | {rate('unauthorized_action_rate')} | "
            f"{rate('benign_task_success_rate')} | {rate('false_blocking_rate')} |"
        )
    lines += [
        "",
        "Trial-level binomial rates include Wilson 95% intervals in report.json. "
        "Repeated deterministic fixtures are not independent statistical samples. "
        "Action-level and episode-level rates have no independence assumption or interval.",
        "",
        "Runtime pairs in report.json compare matching scenario/agent/seed/backend "
        "runs. Short synthetic timings are noisy and do not establish production overhead.",
        "",
        "See config.json for the resolved configuration, versions and scenario hashes; "
        "trials/ contains raw trajectories, scenario snapshots and per-trial metrics.",
        "",
    ]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return report
