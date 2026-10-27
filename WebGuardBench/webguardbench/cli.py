import argparse
import asyncio
import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from uuid import uuid4

import yaml

from . import __version__
from .defenses import Defense
from .evaluator import evaluate_trajectory
from .reporting.reports import save_json, save_reports
from .runner.experiment import run_experiment
from .runner.trajectory import utc_now
from .scenarios.loader import load_document, load_scenario, load_scenarios
from .scenarios.schema import fields, integer


def parser():
    root = argparse.ArgumentParser(description="WebGuardBench security evaluation")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validate scenarios; default: bundled suite")
    validate.add_argument("path", nargs="?")
    run = commands.add_parser("run", help="Run an experiment and export reproducible reports")
    run.add_argument("--config")
    run.add_argument("--scenario", help="Scenario YAML/JSON file or directory")
    run.add_argument("--agent", help="scripted, task-only, json-endpoint or module:factory")
    run.add_argument("--backend", choices=["memory", "browser"])
    run.add_argument("--defenses", help="Comma-separated none,allowlist,actionshield")
    run.add_argument("--trials", type=int, help="Repeats per scenario and defense")
    run.add_argument("--seed", type=int)
    run.add_argument("--max-steps", type=int)
    run.add_argument("--timeout", type=float, dest="timeout_seconds")
    run.add_argument("--output", help="New or empty output directory")
    evaluate = commands.add_parser("evaluate", help="Re-evaluate an exported trajectory")
    evaluate.add_argument("--scenario", required=True)
    evaluate.add_argument("--trajectory", required=True)
    evaluate.add_argument("--output", help="New JSON file; otherwise print metrics")
    return root


def resolve(args):
    config = {}
    config_dir = Path.cwd()
    if args.config:
        config = load_document(args.config)
        config_dir = Path(args.config).resolve().parent
    keys = {
        "scenario",
        "agent",
        "backend",
        "defenses",
        "trials",
        "seed",
        "max_steps",
        "timeout_seconds",
    }
    fields(config, keys, set(), "experiment configuration")
    defaults = {
        "scenario": None,
        "agent": "scripted",
        "backend": "memory",
        "defenses": [{"name": "none"}, {"name": "allowlist"}],
        "trials": 1,
        "seed": 0,
        "max_steps": 50,
        "timeout_seconds": 60.0,
    }
    resolved = {**defaults, **config}
    if resolved["scenario"] is not None:
        if not isinstance(resolved["scenario"], str):
            raise ValueError("scenario must be a path string")
        resolved["scenario"] = str((config_dir / resolved["scenario"]).resolve())
    for key in keys - {"defenses"}:
        value = getattr(args, key)
        if value is not None:
            resolved[key] = value
    if args.defenses is not None:
        resolved["defenses"] = [{"name": name.strip()} for name in args.defenses.split(",")]
    integer(resolved["trials"], "trials", 1, 10000)
    integer(resolved["seed"], "seed", 0, 2**32 - resolved["trials"])
    integer(resolved["max_steps"], "max_steps", 1, 10000)
    timeout = resolved["timeout_seconds"]
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0 < timeout <= 86400
    ):
        raise ValueError("timeout_seconds must be in (0, 86400]")
    if resolved["backend"] not in {"memory", "browser"} or not isinstance(resolved["agent"], str):
        raise ValueError("Invalid backend or agent")
    if not isinstance(resolved["defenses"], list) or not resolved["defenses"]:
        raise ValueError("defenses must be a nonempty list")
    for defense in resolved["defenses"]:
        fields(defense, {"name", "allowed_actions"}, {"name"}, "defense")
    names = [d["name"] for d in resolved["defenses"]]
    if not all(isinstance(n, str) for n in names) or len(names) != len(set(names)):
        raise ValueError("Each defense name must be a unique string")
    return resolved


def provenance():
    versions = {}
    for package in ("PyYAML", "playwright"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    revision = dirty = None
    try:
        project = Path(__file__).resolve().parents[1]
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=project, stderr=subprocess.DEVNULL, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--", "."],
                cwd=project,
                stderr=subprocess.DEVNULL,
                text=True,
            )
        )
    except (OSError, subprocess.CalledProcessError):
        pass
    return {
        "webguardbench": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": versions,
        "git_revision": revision,
        "git_dirty": dirty,
    }


async def run_suite(config, output):
    scenarios = load_scenarios(config["scenario"])
    defenses = [Defense(d["name"], d.get("allowed_actions")) for d in config["defenses"]]
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(
            "Output directory must be new or empty; existing results are never overwritten"
        )
    output.mkdir(parents=True, exist_ok=True)
    experiment_id = uuid4().hex
    info = {
        "experiment_id": experiment_id,
        "started_utc": utc_now(),
        "versions": provenance(),
        "configuration": config,
        "scenario_sha256": {
            s.scenario_id: hashlib.sha256(
                json.dumps(s.to_dict(), sort_keys=True).encode()
            ).hexdigest()
            for s in scenarios
        },
    }
    save_json(info, output / "config.json")
    results = []
    for scenario in scenarios:
        for repeat in range(config["trials"]):
            # Alternate order to reduce systematic warm-up bias in paired timings.
            ordered = defenses if repeat % 2 == 0 else list(reversed(defenses))
            for defense in ordered:
                trajectory = await run_experiment(
                    scenario,
                    config["agent"],
                    defense,
                    backend=config["backend"],
                    seed=config["seed"] + repeat,
                    max_steps=config["max_steps"],
                    timeout_seconds=config["timeout_seconds"],
                )
                result = evaluate_trajectory(scenario, trajectory)
                trial = output / "trials" / trajectory.trial_id
                save_json(scenario.to_dict(), trial / "scenario.json")
                save_json(trajectory.to_dict(), trial / "trajectory.json")
                save_json(result, trial / "metrics.json")
                results.append(result)
                print(
                    f"{scenario.scenario_id} [{defense.name}] seed={trajectory.seed}: "
                    f"{trajectory.status}",
                    flush=True,
                )
                # Keep reports usable even if a later trial is interrupted.
                save_reports(results, output, info)
    info["finished_utc"] = utc_now()
    save_json(info, output / "config.json")
    save_reports(results, output, info)
    print(f"Reports: {output.resolve()}")
    return 0 if all(r["eligible"] for r in results) else 1


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "validate":
            scenarios = load_scenarios(args.path)
            print(
                f"Validated {len(scenarios)} scenario(s): "
                + ", ".join(s.scenario_id for s in scenarios)
            )
            return 0
        if args.command == "evaluate":
            scenario = load_scenario(args.scenario)
            result = evaluate_trajectory(scenario, load_document(args.trajectory))
            if args.output:
                if Path(args.output).exists():
                    raise ValueError("Output file already exists")
                save_json(result, args.output)
            else:
                print(json.dumps(result, indent=2))
            return 0
        config = resolve(args)
        output = Path(args.output or f"results/{uuid4().hex}")
        return asyncio.run(run_suite(config, output))
    except (ValueError, OSError, RuntimeError, yaml.YAMLError) as exc:
        print(f"webguardbench: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Experiment interrupted; completed trial artifacts are preserved", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
