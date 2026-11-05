import argparse
import json

from pathlib import Path

from ac_dpi_pilot.paths import RAW_RESULTS_DIR
from ac_dpi_pilot.runtime import (
    compare_trajectories,
    save_experiment
)


def load_jsonl(path):

    records = []

    with Path(path).open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                records.append(json.loads(line))

    return records


def find_latest_experiment2():

    files = sorted(
        RAW_RESULTS_DIR.glob("experiment2_*_trials.jsonl"),
        key=lambda path: path.stat().st_mtime
    )

    if not files:
        raise FileNotFoundError(
            "No Experiment 2 trial records were found."
        )

    return files[-1]


def main():

    parser = argparse.ArgumentParser(
        description="Experiment 3: Trajectory analysis"
    )

    parser.add_argument(
        "--input",
        default=None,
        help="Optional Experiment 2 JSONL file."
    )

    args = parser.parse_args()

    input_path = (
        Path(args.input)
        if args.input
        else find_latest_experiment2()
    )

    source_records = load_jsonl(input_path)

    results = []

    for record in source_records:

        if record.get("record_type") != "paired_trial":
            continue

        baseline = record["baseline"]
        attack = record["attack"]

        analysis = compare_trajectories(
            baseline,
            attack
        )

        results.append({

            "scenario_id": record["scenario_id"],

            "category": record["category"],

            "baseline_trajectory": baseline["trajectory"],

            "attack_trajectory": attack["trajectory"],

            "analysis": analysis

        })

    if not results:
        raise ValueError(
            "The input file contains no paired Experiment 2 records."
        )

    summary = {

        "source_file": str(input_path),

        "scenario_count": len(results),

        "trajectory_results": results,

        "mean_normalized_divergence": round(
            sum(
                item["analysis"]["normalized_trajectory_divergence"]
                for item in results
            ) / len(results),
            4
        )

    }

    artifacts = save_experiment(
        "experiment3_trajectory_analysis",
        summary,
        results
    )

    print("Experiment 3 completed.")
    print("Source:", input_path)
    print("Summary:", artifacts["summary"])
    print("Raw results:", artifacts["raw"])


if __name__ == "__main__":
    main()
