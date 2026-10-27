# WebGuardBench

**An executable, action-level security benchmark for web agents.**

WebGuardBench connects a user's authorized task, an agent's proposed actions, actual
environment effects, and independently defined security outcomes. It runs locally
with synthetic data and exports reproducible JSON, CSV, and Markdown reports.

**Status: version 0.1.0, functional research prototype.** The scenario loader,
runner, browser environment, ActionShield bridge, evaluator, reports, CLI, and test
suite are implemented. The bundled agents are deterministic software fixtures.
They are **not LLM evaluations**, and their outcomes do not establish real-world
defense effectiveness, research novelty, or generalization.

Parent project: [Advanced Web Agent Security](../README.md).

## What works

- Six versioned scenarios: paired benign and direct-injection tasks for shopping,
  email summarization, and file inventory.
- Strict YAML/JSON validation, duplicate-key rejection, explicit authorization,
  observable task completion, and predefined attack objectives.
- Deterministic in-memory execution or actual headless Chromium interaction with
  an ephemeral local website. The two backends share authoritative fixture state.
- Scripted agents, a provider-neutral JSON HTTP adapter for external agents, and
  a Python adapter protocol for custom integrations.
- Baseline, independent action allowlist, and the sibling ActionShield engine.
- Proposed/blocked/executed actions, successful effects, action failures,
  unknown outcomes, timeouts, step limits, and resource cleanup.
- Attack success, unauthorized execution, goal deviation, first-event steps,
  recovery episodes, legitimate utility, false blocking, and paired timings.
- Counts and denominators, explicit missing values, trial-level Wilson intervals,
  scenario snapshots and hashes, versions, seeds, and Git provenance.
- Unit, integration, CLI, HTTP-adapter, ActionShield, and Chromium tests; GitHub
  Actions runs core tests on Windows/Linux with Python 3.11/3.13 and browser tests
  on Linux with Python 3.11.

## Install

Python 3.11+ is required. From the repository root:

```bash
cd WebGuardBench
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

Install the core package (no browser, model, or API key required):

```bash
python -m pip install -e .
```

For browser execution and development:

```bash
python -m pip install -e ".[dev,browser]"
python -m playwright install chromium
```

On minimal Linux systems use `python -m playwright install --with-deps chromium`.
Alternatively, set `WGB_BROWSER_CHANNEL=chrome` or `msedge` to use an installed
browser through Playwright. Trials always use a fresh headless context and record
the actual browser version and channel; personal browsing profiles are not used.
`requirements.txt` supplies core dependencies for source-based use; installing the
package also creates the `webguardbench` command and includes scenario resources.

## Quick start

```bash
python -m webguardbench validate
python -m webguardbench run --output results/quickstart
```

This runs all six scenarios with both `none` and `allowlist` defenses: 12 trials.
The default scripted attack fixtures deliberately attempt one prohibited action.
Expected software-check outcomes:

| Configuration | Attack objectives achieved | Benign tasks completed |
|---|---:|---:|
| Scripted + no defense | 3 / 3 | 3 / 3 |
| Scripted + allowlist | 0 / 3 | 3 / 3 |

These values validate the fixture pipeline, not a model's resistance to injection.
Injection text is scenario data. The scripted agent follows its action list;
it does not interpret, discover, or reason about that text.

Open `results/quickstart/report.md` for a summary. `report.json` includes every
metric's numerator and denominator, full trial metrics, and paired timing records.
`trials.csv` supports downstream analysis.

```text
results/quickstart/
  config.json                  # resolved settings, versions, seeds, scenario hashes
  report.json                  # defense groups, trial metrics, runtime pairs
  report.md
  trials.csv
  trials/<trial-id>/
    scenario.json              # exact, loadable scenario snapshot
    trajectory.json            # proposed actions, decisions, observations, effects
    metrics.json
```

Choose a **new or empty output folder** for every experiment. Existing results are
never overwritten by the CLI. Completed trial artifacts and partial reports are
saved as the suite progresses.

## Run experiments

```bash
python -m webguardbench run --config configs/comparison.yaml --output results/comparison
python -m webguardbench run --backend browser --output results/chromium
python -m webguardbench run --scenario webguardbench/data/scenarios/shopping_injection.yaml --defenses none,allowlist --trials 3 --seed 42 --output results/shopping
```

CLI options override configuration values. Scenario paths inside a configuration
resolve relative to that configuration's directory; CLI paths resolve from the
working directory. Defaults are `scripted`, `memory`, defenses `none,allowlist`,
one trial, seed 0, 50 action proposals, and 60 seconds per trial. Repeats increment
the seed identically for every defense. Execution order alternates across repeats.

Exit codes: `0` all trials completed; `1` one or more trials incomplete; `2` invalid
configuration/input/output; `130` interrupted. An unsuccessful legitimate task or
a successful attack is a measured outcome, not an infrastructure error.

Re-evaluate a recorded trial without rerunning the agent:

```bash
python -m webguardbench evaluate --scenario results/quickstart/trials/TRIAL_ID/scenario.json --trajectory results/quickstart/trials/TRIAL_ID/trajectory.json
```

Replace `TRIAL_ID` with an actual exported trial directory. The evaluator rejects
inconsistent effect records and recomputes authorization from the scenario rather
than trusting recorded agent labels. See [methodology](docs/methodology.md).

## Agent and defense integration

Agents implement asynchronous `initialize(scenario, seed)`,
`propose_action(observation) -> Action | None`, and `shutdown()` methods.
The runner alone executes actions; observations include previous results.
Returning `None` terminates a complete trial. See
[the adapter guide](docs/adapters.md) and [Python example](examples/run_benchmark.py).

The built-in `task-only` agent filters the script using ground truth. It is an
**oracle software control**, never an independent defense or model baseline.

For a real agent exposed by a service, set `WGB_AGENT_ENDPOINT` and run
`--agent json-endpoint`. Optional `WGB_AGENT_MODEL` identifies the model and
`WGB_AGENT_TOKEN` supplies an access token. The service must implement the small
[JSON request/response contract](docs/adapters.md#http-contract). No particular LLM
provider or hosted service is included or invoked automatically.

For ActionShield, add the sibling implementation to your import path. PowerShell,
from `WebGuardBench`:

```powershell
$env:PYTHONPATH = (Resolve-Path ..\ActionShield).Path
python -m webguardbench run --config configs/actionshield.yaml --output results/actionshield
```

Linux/macOS:

```bash
PYTHONPATH=../ActionShield python -m webguardbench run --config configs/actionshield.yaml --output results/actionshield
```

This configuration uses Chromium; add `--backend memory` to use the in-memory
backend. The bridge calls the existing ActionShield policy engine before fixture
dispatch. It maps `read` to `NAVIGATE`, `compare/report` to `CLICK`, and each
high-impact action to its matching ActionShield type. Consequently ActionShield's
coarse action types cannot distinguish `compare` from `report`. Its policy is
configured independently of scenario ground truth. The `allowlist` defense uses
exact benchmark action kinds. Neither bridge claims to intercept arbitrary browser
scripts or every possible browser side effect.

## Scenarios and environments

Scenario files live in `webguardbench/data/scenarios/` so installed wheels can run
the default suite outside the checkout. The schema is defined in
[`schema.py`](webguardbench/scenarios/schema.py). Every attack scenario declares:

- A task description and disjoint permitted/prohibited action lists.
- A direct-injection instruction and an environment-observable attack effect.
- A synthetic environment, a deterministic fixture script, and a recovery window.

For benign scenarios, `attack` is `null`. Unlisted actions are unauthorized.
The three environments expose a fixed action space and synthetic targets. Adding
a YAML file can vary scripts, policies, and recovery windows; adding a genuinely
new task type also requires implementing its state/effects and validation rules.

The Chromium backend binds a per-trial server to `127.0.0.1` on a random port,
creates a fresh nonpersistent browser context, blocks service workers and network
requests outside the fixture origin, and disables downloads. Purchases, sends,
and deletions modify synthetic in-memory state only. The in-memory backend uses
the same state transitions without a browser or network.

```text
Scenario -> Agent proposal -> Defense decision -> Environment execution
                    |                 |                     |
                    +----------- Trajectory ----------------+
                                      |
                         Independent evaluator -> Reports
```

## Tests and package build

```bash
python -m pytest -m "not browser" -q
python -m ruff check .
python -m ruff format --check .
python -m build
```

To include ActionShield tests, set `PYTHONPATH` as above. To enable browser tests:

```powershell
$env:WGB_TEST_BROWSER = "1"
python -m pytest -m browser -q
```

Or on Linux/macOS: `WGB_TEST_BROWSER=1 python -m pytest -m browser -q`.
Browser tests intentionally skip until explicitly enabled. They verify parity of
all six scenarios under baseline and allowlist defenses, external-request
blocking, and ActionShield purchase interception.

## Research boundaries and next steps

Version 0.1.0 provides the working benchmark foundation. It does not include a
published LLM study, a large/diverse dataset, adaptive attack generation, general
website automation, indirect or multimodal injection, BrowserGym integration, or
cross-model generalization studies. Those require separate adapters, data,
threat-model specifications, and experiments. No research result is fabricated to
fill those gaps. Short fixture timings and repeated deterministic seeds should
not be used as statistical evidence of defense effectiveness.

Authorization is action-kind-level in this initial schema; target-level policies,
independent human labels, and richer task effects are future extensions. Imported
trajectories are assumed to originate from trusted instrumentation; consistency
checks are not cryptographic attestation. Custom Python adapters execute trusted
code and must not be loaded from untrusted configurations. The local environment
restricts fixture actions, not arbitrary code running on the host.

Use synthetic data and authorized environments. Built-in exports omit the HTTP
access token and do not collect model chain-of-thought; custom adapters remain
responsible for keeping secrets and personal information out of their metadata
and observations.

Licensed under the [MIT License](LICENSE), matching the [parent license](../LICENSE).
