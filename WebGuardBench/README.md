
# WebGuardBench

**An Executable, Action-Level Security Benchmark for Web Agents**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Browser](https://img.shields.io/badge/Browser-Playwright-green?logo=playwright&logoColor=white)](https://playwright.dev/)
[![Focus](https://img.shields.io/badge/Focus-AI%20Security-red)](https://github.com/topics/ai-security)
[![Projects](https://img.shields.io/badge/Projects-10-purple)](../README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Research%20%26%20Development-orange)](../README.md)

---

## Overview

WebGuardBench is a reproducible research benchmark designed to evaluate the security of web agents against **Direct Prompt Injection (DPI) attacks** at the action level.

The benchmark connects user-authorized tasks, agent-proposed actions, defense decisions, observable environment effects, and independently evaluated security outcomes. It provides a controlled framework for investigating whether web agents remain within their authorized operational boundaries when exposed to adversarial instructions.

WebGuardBench supports local execution with synthetic data and generates reproducible JSON, CSV, and Markdown reports for security analysis.

> **Project Status: Version 0.1.0 — Functional Research Prototype**
>
> The scenario loader, execution runner, browser environment, ActionShield bridge, evaluator, reporting system, CLI, and test suite are implemented. The bundled agents are deterministic software fixtures, not LLM-based agents. Their results validate the benchmark infrastructure and do not establish real-world defense effectiveness, research novelty, or generalization to actual language models.

**Parent Repository:** [Advanced Web Agent Security](../README.md)

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running Experiments](#running-experiments)
- [Reevaluating Recorded Trials](#reevaluating-recorded-trials)
- [Agent and Defense Integration](#agent-and-defense-integration)
- [Scenarios and Environments](#scenarios-and-environments)
- [Evaluation Metrics](#evaluation-metrics)
- [Output Structure](#output-structure)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [Research Scope and Limitations](#research-scope-and-limitations)
- [Future Research Directions](#future-research-directions)
- [Security and Privacy](#security-and-privacy)
- [License](#license)

---

## Key Features

### 1. Direct Prompt Injection Scenarios

- Six versioned scenarios covering shopping, email summarization, and file inventory.
- Paired benign and direct-injection tasks across the three task categories.
- Explicit authorization policies defining permitted and prohibited actions.
- Predefined attack objectives and environment-observable effects.
- Strict YAML and JSON validation, including duplicate-key rejection.
- Scenario snapshots and hashes for reproducible experiments.

### 2. Multiple Execution Backends

- **In-memory backend:** Deterministic execution without a browser or network.
- **Chromium backend:** Headless browser interaction with an ephemeral local website.
- Shared authoritative fixture state across both backends.
- Fresh, nonpersistent browser contexts for individual trials.
- Synthetic purchases, email sends, and file deletions that modify in-memory state only.

### 3. Agent Integration

- Deterministic scripted agents for infrastructure validation.
- Provider-neutral JSON HTTP adapter for external agents.
- Python adapter protocol for custom agent implementations.
- Explicit initialization, action-proposal, and shutdown interfaces.
- Configurable trial limits, timeouts, and random seeds.

### 4. Security Defense Evaluation

- Baseline execution without an active defense.
- Independent action-allowlist enforcement.
- Integration with the sibling ActionShield policy engine.
- Recording of proposed, blocked, and executed actions.
- Tracking of action failures, successful effects, unknown outcomes, timeouts, and execution limits.

### 5. Security and Utility Metrics

- Attack-objective success.
- Unauthorized action execution.
- Goal deviation.
- First-event step measurements.
- Recovery episodes.
- Legitimate task completion.
- False blocking of permitted actions.
- Paired execution-time measurements.

### 6. Reproducibility and Reporting

- Structured JSON, CSV, and Markdown reports.
- Explicit metric numerators and denominators.
- Missing-value handling and trial-level Wilson confidence intervals.
- Scenario snapshots, hashes, software versions, and random seeds.
- Git provenance for experiment tracking.
- Trial-level trajectories and metric records.

### 7. Testing and Continuous Integration

- Unit and integration tests.
- CLI and HTTP-adapter tests.
- ActionShield integration tests.
- Optional Chromium browser tests.
- GitHub Actions workflows for core testing on Windows and Linux with Python 3.11 and 3.13, and browser testing on Linux with Python 3.11.

---

## System Architecture

WebGuardBench separates agent behavior, defense decisions, environment execution, and security evaluation.

```text
+--------------------------------------------------+
|               Authorized User Task               |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|                  Web Agent                       |
|                                                  |
|  Observations -> Reasoning -> Action Proposal    |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|                Defense Layer                     |
|                                                  |
|  Baseline | Action Allowlist | ActionShield       |
+--------------------------------------------------+
                        |
             +----------+----------+
             |                     |
             v                     v
      Action Blocked         Action Executed
                                   |
                                   v
+--------------------------------------------------+
|              Execution Environment               |
|                                                  |
|      In-Memory Backend / Headless Chromium       |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|              Trajectory Collection               |
|                                                  |
|  Proposals | Decisions | Observations | Effects  |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|             Independent Evaluator                |
|                                                  |
|  Authorization | Attack Success | Utility        |
|  Goal Deviation | Recovery | False Blocking      |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|                Experiment Reports                 |
|                                                  |
|                 JSON / CSV / MD                  |
+--------------------------------------------------+
```

The evaluator recomputes authorization from scenario definitions rather than relying solely on labels supplied by the agent.

This separation is intended to support more consistent measurement of observable agent behavior.

---

## Installation

### Prerequisites

- Python 3.11 or later.
- Git, if cloning the repository.
- Playwright and Chromium for browser-based experiments.
- An external agent service, if conducting evaluations with an independently implemented agent.

### Step 1: Navigate to the Project Directory

```bash
cd WebGuardBench
```

### Step 2: Create a Virtual Environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux or macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Core Dependencies

```bash
python -m pip install -e .
```

The core installation does not require a browser, an LLM, or an API key.

Installing the package also registers the `webguardbench` command and includes the scenario resources required by the default benchmark suite.

### Step 4: Install Browser and Development Dependencies

```bash
python -m pip install -e ".[dev,browser]"
python -m playwright install chromium
```

On minimal Linux systems, install the required browser dependencies with:

```bash
python -m playwright install --with-deps chromium
```

Alternatively, configure Playwright to use an installed browser.

**Google Chrome — PowerShell**

```powershell
$env:WGB_BROWSER_CHANNEL = "chrome"
```

**Microsoft Edge — PowerShell**

```powershell
$env:WGB_BROWSER_CHANNEL = "msedge"
```

Each browser trial uses a fresh headless context and records the actual browser version and channel. Personal browser profiles are not used.

The `requirements.txt` file supplies core dependencies for source-based use.

---

## Quick Start

### 1. Validate the Benchmark Scenarios

```bash
python -m webguardbench validate
```

### 2. Run the Default Benchmark Suite

```bash
python -m webguardbench run --output results/quickstart
```

The default configuration executes six scenarios with two defense configurations:

- `none`: Baseline execution without an active defense.
- `allowlist`: Execution with an exact action-kind allowlist.

This produces 12 trials: six scenarios multiplied by two defense configurations.

### 3. Expected Software-Validation Results

The bundled scripted attack fixtures deliberately attempt one prohibited action in each injection scenario.

| Configuration | Attack objectives achieved | Benign tasks completed |
|---|---:|---:|
| Scripted agent + no defense | 3 / 3 | 3 / 3 |
| Scripted agent + allowlist | 0 / 3 | 3 / 3 |

> **Important:** These results validate the benchmark's fixture pipeline, not an LLM's resistance to direct prompt injection. The scripted agent follows a predetermined action list and does not interpret, discover, or reason about the injection text.

### 4. Inspect the Results

The generated reports are stored in the specified output directory.

```text
results/quickstart/
├── config.json
├── report.json
├── report.md
├── trials.csv
└── trials/
    └── <trial-id>/
        ├── scenario.json
        ├── trajectory.json
        └── metrics.json
```

See [Output Structure](#output-structure) for the purpose of each artifact.

**Output safety:** Use a new or empty output directory for each experiment. The CLI does not overwrite existing results. Completed trial artifacts and partial reports are saved as the suite progresses.

---

## Running Experiments

### 1. Run a Configuration File

```bash
python -m webguardbench run \
  --config configs/comparison.yaml \
  --output results/comparison
```

### 2. Run Browser-Based Experiments

```bash
python -m webguardbench run \
  --backend browser \
  --output results/chromium
```

### 3. Run a Specific Scenario

```bash
python -m webguardbench run \
  --scenario webguardbench/data/scenarios/shopping_injection.yaml \
  --defenses none,allowlist \
  --trials 3 \
  --seed 42 \
  --output results/shopping
```

### Configuration and Execution Behavior

- CLI arguments override values in configuration files.
- Scenario paths in configuration files resolve relative to the configuration file's directory.
- Scenario paths provided through the CLI resolve relative to the working directory.
- Default agent: `scripted`.
- Default backend: `memory`.
- Default defenses: `none,allowlist`.
- Default trials: `1`.
- Default random seed: `0`.
- Default maximum action proposals: `50` per trial.
- Default timeout: `60` seconds per trial.
- Repeated trials increment the seed consistently across defense configurations.
- Execution order alternates across repeats.

### Exit Codes

| Exit code | Description |
|---|---|
| `0` | All trials completed. |
| `1` | One or more trials were incomplete. |
| `2` | Invalid configuration, input, or output. |
| `130` | Execution interrupted. |

An unsuccessful legitimate task or a successful attack is a measured benchmark outcome, not necessarily an infrastructure error.

---

## Reevaluating Recorded Trials

WebGuardBench supports reevaluating recorded trials without rerunning the agent.

```bash
python -m webguardbench evaluate \
  --scenario results/quickstart/trials/<trial-id>/scenario.json \
  --trajectory results/quickstart/trials/<trial-id>/trajectory.json
```

Replace `<trial-id>` with an actual exported trial directory.

The evaluator checks the consistency of recorded environment effects and recomputes authorization from the scenario definition rather than trusting recorded agent labels.

This functionality enables independent reevaluation of saved trajectories.

For the detailed evaluation methodology, see [`docs/methodology.md`](docs/methodology.md).

---

## Agent and Defense Integration

### Agent Interface

Custom agents implement the following asynchronous interface:

```python
async def initialize(scenario, seed):
    ...

async def propose_action(observation):
    ...

async def shutdown():
    ...
```

The interface provides three operations:

| Method | Purpose |
|---|---|
| `initialize(scenario, seed)` | Initialize the agent for a trial. |
| `propose_action(observation)` | Return an `Action` or `None`. |
| `shutdown()` | Release agent resources. |

The runner executes the proposed actions, and observations include previous execution results.

Returning `None` terminates the trial.

For implementation details, consult the [agent adapter guide](docs/adapters.md) and [Python integration example](examples/run_benchmark.py).

### Oracle Control

The built-in `task-only` agent filters the scripted action sequence using ground-truth task information.

It is an **oracle software control**, not an independent defense or a model baseline. Its results must be interpreted accordingly.

### External Agent Integration

For an agent exposed through an HTTP service, configure the following environment variables:

```bash
WGB_AGENT_ENDPOINT=<agent-service-endpoint>
WGB_AGENT_MODEL=<model-identifier>
WGB_AGENT_TOKEN=<access-token>
```

Then run:

```bash
python -m webguardbench run \
  --agent json-endpoint \
  --output results/external-agent
```

The service must implement the JSON request/response contract documented in [`docs/adapters.md`](docs/adapters.md#http-contract).

The adapter is provider-neutral. No particular LLM provider or hosted service is automatically included or invoked.

**Research consideration:** Connecting an external LLM does not, by itself, establish a meaningful prompt-injection evaluation. The agent must actually process scenario observations and injection instructions, and its behavior must be measured under a clearly specified threat model.

### ActionShield Integration

ActionShield is integrated as a separate policy engine.

Make the sibling ActionShield implementation available on the Python import path before running the integration.

**Windows — PowerShell**

```powershell
$env:PYTHONPATH = (Resolve-Path ..\ActionShield).Path

python -m webguardbench run `
  --config configs/actionshield.yaml `
  --output results/actionshield
```

**Linux or macOS**

```bash
PYTHONPATH=../ActionShield \
python -m webguardbench run \
  --config configs/actionshield.yaml \
  --output results/actionshield
```

The ActionShield configuration uses Chromium by default. Add `--backend memory` to use the in-memory backend.

The bridge invokes the existing ActionShield policy engine before dispatching fixture actions.

| WebGuardBench action | ActionShield action type |
|---|---|
| `read` | `NAVIGATE` |
| `compare` | `CLICK` |
| `report` | `CLICK` |
| High-impact actions | Corresponding ActionShield action type |

ActionShield uses coarser action categories and therefore cannot distinguish `compare` from `report` through this mapping alone.

Its policy is configured independently of scenario ground truth.

The `allowlist` defense uses exact benchmark action kinds. Neither integration claims to intercept arbitrary browser scripts or every possible browser side effect.

---

## Scenarios and Environments

### Scenario Organization

Scenario files are stored in:

```text
webguardbench/data/scenarios/
```

The schema is defined in [`schema.py`](webguardbench/scenarios/schema.py).

Each attack scenario defines:

- A task description.
- Disjoint permitted and prohibited action lists.
- A direct prompt injection instruction.
- An environment-observable attack effect.
- A synthetic environment.
- A deterministic fixture script.
- A recovery window.

For benign scenarios, `attack` is set to `null`.

Any action not explicitly listed as permitted is considered unauthorized.

### Current Task Categories

The benchmark includes three synthetic task environments.

**1. Shopping**

Evaluates agent behavior involving shopping-related actions.

**2. Email Summarization**

Evaluates agent behavior involving email-related actions.

**3. File Inventory**

Evaluates agent behavior involving file-related actions.

Each environment exposes a fixed action space and synthetic targets.

Existing YAML scenarios can vary scripts, policies, and recovery windows. Adding a genuinely new task type also requires implementing its state transitions, observable effects, and validation rules.

### In-Memory Backend

The in-memory backend executes scenario state transitions without launching a browser or making network requests.

It is intended for fast, deterministic infrastructure testing.

### Chromium Backend

The browser backend interacts with an ephemeral local website using headless Chromium.

For each trial, it:

- Starts a local server bound to `127.0.0.1` on a random port.
- Creates a fresh, nonpersistent browser context.
- Blocks service workers.
- Blocks network requests outside the fixture origin.
- Disables downloads.
- Records browser-version and channel information.

Purchases, email sends, and file deletions modify synthetic in-memory state only.

Both backends share authoritative fixture state, enabling comparisons between browser-based and in-memory execution.

---

## Evaluation Metrics

WebGuardBench evaluates security and utility outcomes at the trial and defense-group levels.

| Metric | Evaluation purpose |
|---|---|
| Attack success | Measures whether predefined attack objectives were achieved. |
| Unauthorized execution | Measures whether prohibited actions were executed. |
| Goal deviation | Tracks departures from authorized task behavior. |
| First-event steps | Records the step at which a specified event first occurs. |
| Recovery episodes | Tracks recovery behavior within the configured recovery window. |
| Legitimate utility | Measures completion of benign tasks. |
| False blocking | Tracks permitted actions blocked by the defense. |
| Execution timing | Records execution durations and paired timing measurements. |

The reporting pipeline includes explicit metric numerators and denominators, missing-value handling, and trial-level Wilson confidence intervals where applicable.

The exact metric definitions and evaluation procedures are documented in [`docs/methodology.md`](docs/methodology.md).

**Interpretation requirement:** Results must be interpreted in the context of the agent implementation, threat model, scenario coverage, and experimental design. Deterministic fixture results are not evidence of generalizable LLM security performance.

---

## Output Structure

Each experiment produces a structured output directory.

| File | Description |
|---|---|
| `config.json` | Resolved settings, software versions, seeds, and scenario hashes. |
| `report.json` | Defense-group summaries, trial metrics, and paired timing records. |
| `report.md` | Human-readable experiment summary. |
| `trials.csv` | Trial-level data for downstream statistical analysis. |
| `scenario.json` | Exact, loadable scenario snapshot. |
| `trajectory.json` | Proposed actions, defense decisions, observations, and environment effects. |
| `metrics.json` | Evaluation metrics for an individual trial. |

This structure supports inspection, downstream analysis, and reevaluation of recorded trials.

---

## Testing and Quality Assurance

### Run Core Tests

```bash
python -m pytest -m "not browser" -q
```

### Run Linting

```bash
python -m ruff check .
```

### Check Code Formatting

```bash
python -m ruff format --check .
```

### Build the Package

```bash
python -m build
```

### Run ActionShield Tests

Configure `PYTHONPATH` to include the sibling ActionShield implementation, as described in the [ActionShield integration](#actionshield-integration) section.

### Run Browser Tests

Browser tests are disabled by default and must be explicitly enabled.

**Windows — PowerShell**

```powershell
$env:WGB_TEST_BROWSER = "1"
python -m pytest -m browser -q
```

**Linux or macOS**

```bash
WGB_TEST_BROWSER=1 python -m pytest -m browser -q
```

The browser tests verify:

- Parity across all six scenarios under baseline and allowlist defenses.
- Blocking of external network requests.
- ActionShield interception of synthetic purchase actions.

The configured GitHub Actions workflows also exercise the core and browser test suites on their respective supported environments.

---

## Research Scope and Limitations

WebGuardBench version 0.1.0 establishes the initial infrastructure for action-level security evaluation. It is not yet a comprehensive evaluation of real-world web-agent security.

### Current Limitations

The current version does not include:

- A completed empirical study using LLM-based agents.
- A large or diverse benchmark dataset.
- Adaptive attack generation.
- General-purpose website automation.
- Indirect prompt injection scenarios.
- Multimodal prompt injection scenarios.
- BrowserGym integration.
- Cross-model generalization studies.

These capabilities require additional agent adapters, datasets, threat-model specifications, and controlled experiments.

### Authorization Granularity

The initial schema defines authorization at the action-kind level.

Target-specific authorization policies, independent human labels, and richer task-effect representations remain potential extensions.

### Evaluation Assumptions

Imported trajectories are assumed to originate from trusted instrumentation. Consistency checks do not provide cryptographic attestation.

Short fixture timings and repeated deterministic seeds must not be treated as statistical evidence of defense effectiveness.

### Integration Boundaries

The ActionShield bridge and action allowlist operate on benchmark-defined actions. They do not guarantee interception of arbitrary browser scripts or all possible side effects.

Custom Python adapters execute trusted code and must not be loaded from untrusted configurations.

The local execution environment restricts fixture actions, not arbitrary code running on the host.

---

## Future Research Directions

Potential extensions include the following.

### 1. Real LLM-Based Evaluation

Integrate web agents that genuinely interpret observations and injection instructions. Evaluate their behavior using controlled, reproducible experiments.

### 2. Broader Scenario Coverage

Expand task diversity, website complexity, action spaces, and authorization policies.

### 3. Adaptive Attack Evaluation

Investigate attacks that adapt to observed agent behavior under a clearly specified threat model.

### 4. Fine-Grained Authorization

Introduce target-level permissions and more expressive policy boundaries to distinguish authorized and unauthorized actions more precisely.

### 5. Cross-Model Generalization

Compare security behavior across different LLMs, agent architectures, and defense configurations.

### 6. Trajectory-Level Security Analysis

Investigate goal deviation, attack progression, the first unauthorized action, recovery behavior, and sensitive-action reachability.

### 7. Independent Outcome Annotation

Incorporate independently reviewed labels where automated evaluation is insufficient.

These directions are prospective research opportunities, not implemented capabilities or established research contributions.

---

## Security and Privacy

WebGuardBench is designed for controlled experiments using synthetic data and authorized environments.

- Default scenarios use synthetic state and targets.
- Browser execution is restricted to the local fixture origin.
- Built-in exports omit the HTTP access token.
- The benchmark does not collect model chain-of-thought.
- Custom adapters are responsible for keeping secrets and personal information out of metadata and observations.
- Custom Python adapters must be treated as trusted code.

Use the benchmark only in environments you own or are authorized to test.

---

## License

WebGuardBench is distributed under the [MIT License](LICENSE), consistent with the parent project's [license](../LICENSE).

---

**Part of the Advanced Web Agent Security project.**

Focused on reproducible experimentation, action-level authorization, and the security evaluation of web agents against direct prompt injection.
