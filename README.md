# Advanced Web Agent Security

**A collection of research and engineering projects dedicated to securing LLM-based Web Agents against direct prompt injection, unauthorized actions, privacy violations, and excessive agency.**

Advanced Web Agent Security is a unified repository containing multiple complementary projects for developing, evaluating, and improving the security of Large Language Model (LLM)-based Web Agents.

The repository brings together runtime security enforcement, goal-conditioned action verification, security benchmarking, sensitive data protection, human approval mechanisms, memory security, attack-defense evaluation, and least-privilege browser permissions.

Each project addresses a specific security problem while contributing to the broader goal of building safer, more reliable, and more trustworthy Web Agents.

> **Project status:** Research and development. Projects are developed and evaluated incrementally. Features, supported configurations, and experimental results will be documented as they become available.

---

## Table of Contents

- [Overview](#overview)
- [Research Motivation](#research-motivation)
- [Project Collection](#project-collection)
  - [ActionShield](#1-actionshield)
  - [WebGuardBench](#2-webguardbench)
  - [GoalGuard](#3-goalguard)
  - [LeakGuard](#4-leakguard)
  - [SafeClick](#5-safeclick)
  - [MemoryShield](#6-memoryshield)
  - [RedBlue Lab](#7-redblue-lab)
  - [WebPermit](#8-webpermit)
- [Overall Architecture](#overall-architecture)
- [Research Directions](#research-directions)
- [Evaluation Metrics](#evaluation-metrics)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Development Roadmap](#development-roadmap)
- [Security and Responsible Use](#security-and-responsible-use)
- [Reproducibility](#reproducibility)
- [Contributing](#contributing)
- [Research and Publications](#research-and-publications)
- [License](#license)

---

## Overview

LLM-based Web Agents can interpret natural-language instructions, inspect websites, plan tasks, interact with browser interfaces, and execute actions on behalf of users.

However, connecting language models to browser actions introduces security risks that extend beyond ordinary text generation.

An agent may follow adversarial instructions, deviate from its authorized goal, execute unintended actions, expose sensitive information, or retain untrusted instructions in persistent memory.

This repository explores these challenges through eight projects.

| No. | Project | Primary Focus |
|---:|---|---|
| 1 | ActionShield | Runtime security and action enforcement |
| 2 | WebGuardBench | Web Agent security benchmarks |
| 3 | GoalGuard | Goal-conditioned action verification |
| 4 | LeakGuard | Sensitive data exfiltration prevention |
| 5 | SafeClick | Risk-aware human approval |
| 6 | MemoryShield | Persistent memory security |
| 7 | RedBlue Lab | Attack-defense experimentation |
| 8 | WebPermit | Least-privilege browser permissions |

The projects are designed to be independently understandable while sharing relevant components, including browser interfaces, security policies, logging utilities, and evaluation tools.

The repository is intended to support practical implementation, security experimentation, reproducible evaluation, and future research publications.

## Research Motivation

### Why Web Agent Security Matters

A Web Agent does more than generate text. It can translate model outputs into actions that affect websites, accounts, applications, and external services.

Important security challenges include:

- **Direct Prompt Injection:** Adversarial instructions attempt to redirect the agent or override the user's intended task.
- **Goal Hijacking:** The agent deviates from its authorized objective.
- **Unauthorized Actions:** The agent executes operations outside the permissions granted by the user.
- **Excessive Agency:** The agent possesses capabilities beyond those required for its task.
- **Sensitive Data Exfiltration:** Private information is disclosed to unauthorized destinations.
- **Persistent Memory Contamination:** Untrusted instructions influence future agent behavior.
- **Insufficient Security Evaluation:** A defense performs well in familiar scenarios but fails under different tasks or attack conditions.

The central motivation of this repository is to investigate how these failures can be detected, prevented, measured, and understood.

---

# Project Collection

## 1. ActionShield

**Runtime Security and Action Enforcement for Web Agents**

### Objective

ActionShield focuses on intercepting proposed browser actions and checking them against security policies before execution.

Instead of relying exclusively on the language model to reject malicious instructions, the system introduces an independent enforcement layer between the agent and the browser.

### Planned Features

- Browser action interception.
- Authorization checks for clicks, typing, navigation, and form submissions.
- Policy-based action enforcement.
- Risk assessment for sensitive operations.
- Human approval for selected high-impact actions.
- Structured security logs.
- Integration with GoalGuard and WebPermit.

### Example

A user asks an agent to compare three laptops. A webpage instructs the agent to purchase one immediately.

ActionShield should reject the purchase when it falls outside the user's authorization while allowing legitimate comparison tasks to continue.

### Research Direction

Investigate whether runtime action enforcement reduces unauthorized actions while preserving legitimate task completion.

---

## 2. WebGuardBench

**A Benchmarking Framework for Web Agent Security**

### Objective

WebGuardBench focuses on reproducible evaluation of Web Agent security failures and defense mechanisms.

### Planned Features

- Controlled browser tasks and test websites.
- Direct prompt-injection scenarios.
- Agent trajectory collection.
- Security and utility metrics.
- Baseline and defense comparisons.
- Experiment configuration management.
- Reproducible evaluation reports.

### Example

Evaluate multiple Web Agents under controlled adversarial instructions and compare their task outcomes, executed actions, authorization violations, and recovery behavior.

### Research Direction

Investigate how security effectiveness varies across agents, tasks, attack conditions, and defense configurations.

---

## 3. GoalGuard

**Goal-Conditioned Action Verification**

### Objective

GoalGuard focuses on verifying whether proposed browser actions are consistent with the user's original objective and explicit permissions.

An action may appear reasonable in isolation but still violate the user's intended task.

### Planned Features

- Explicit task requirement representation.
- Proposed-action verification.
- Goal-deviation detection.
- Browser-state-aware checks.
- Action authorization analysis.
- Security decision explanations.
- Integration with runtime enforcement.

### Example

The user asks an agent to compare hotel prices. A webpage instructs the agent to reserve a non-refundable room.

GoalGuard should identify that making a reservation is outside the requested comparison unless the user has separately authorized it.

### Research Direction

Investigate whether goal-conditioned verification can identify unauthorized actions more effectively than prompt-level filtering alone.

---

## 4. LeakGuard

**Sensitive Data Exfiltration Prevention**

### Objective

LeakGuard focuses on preventing unauthorized disclosure of sensitive information during Web Agent execution.

### Planned Features

- Identification of synthetic sensitive test data.
- Monitoring of supported data-entry and submission operations.
- Destination-aware disclosure policies.
- Data-flow monitoring.
- Unauthorized transfer detection.
- Privacy evaluation and security logging.

### Example

An agent is authorized to inspect profile information but is not authorized to transmit it to an unrelated external website.

LeakGuard should prevent the unauthorized transfer while preserving permitted operations.

### Research Direction

Investigate whether data-flow controls can reduce unauthorized disclosure without unnecessarily restricting legitimate tasks.

---

## 5. SafeClick

**Risk-Aware Human Approval for Web Agents**

### Objective

SafeClick focuses on deciding when an agent may proceed automatically, when it should request explicit approval, and when an action should be blocked.

### Planned Features

- Browser action risk classification.
- Configurable confirmation policies.
- Approval workflows.
- Sensitive-action detection.
- Human-readable action summaries.
- Security and usability evaluation.

### Example

An agent may browse websites and compare products automatically but require user approval before purchasing an item or changing account settings.

### Research Direction

Investigate how risk-aware approval mechanisms can reduce unauthorized actions while minimizing unnecessary interruptions.

---

## 6. MemoryShield

**Security and Provenance for Web Agent Memory**

### Objective

MemoryShield focuses on protecting persistent agent memory from untrusted instructions and information.

### Planned Features

- Information provenance tracking.
- Trusted and untrusted information labels.
- Memory-write authorization policies.
- Detection of suspicious persistent instructions.
- Separation of user-approved preferences from webpage content.
- Cross-session security evaluation.

### Example

An agent encounters an adversarial instruction during one browsing session that attempts to influence future sessions.

MemoryShield should prevent untrusted webpage content from becoming an authoritative persistent instruction.

### Research Direction

Investigate whether provenance-aware memory controls can reduce persistent prompt-injection risks without preventing useful information retention.

---

## 7. RedBlue Lab

**Controlled Attack and Defense Evaluation**

### Objective

RedBlue Lab provides an isolated environment for evaluating Web Agent attacks and comparing defensive mechanisms.

### Planned Features

- Controlled prompt-injection scenarios.
- Configurable adversarial conditions.
- Attack and defense comparisons.
- Agent trajectory analysis.
- Defense configuration management.
- Automated experiment reports.
- Security regression testing.

### Example

Evaluate an agent without an additional defense and then with different security mechanisms enabled.

Compare attack success, unauthorized actions, legitimate task completion, and execution overhead.

### Research Direction

Investigate which conditions expose weaknesses in existing defenses and whether improved mechanisms generalize to previously unseen scenarios.

All experiments should be conducted in authorized, controlled environments.

---

## 8. WebPermit

**Least-Privilege Browser and Tool Authorization**

### Objective

WebPermit focuses on limiting an agent to the browser capabilities required for its current task.

### Planned Features

- Explicit browser permission policies.
- Task-scoped authorization.
- Website-scoped authorization.
- Permissions for reading, typing, submitting, downloading, and modifying information.
- Runtime authorization checks.
- Permission-denial logging.
- Policy testing and auditing.

### Example

An agent authorized to read product information should not automatically receive permission to purchase products or modify account settings.

WebPermit should reject operations outside the granted permission scope.

### Research Direction

Investigate how least-privilege controls can limit the impact of prompt injection, even when the underlying model proposes an unauthorized action.

---

# Overall Architecture

The projects address different parts of the Web Agent security lifecycle.

```text
                     USER TASK
                         |
                         v
              +----------------------+
              |   LLM-Based Agent    |
              |                      |
              | Observe              |
              | Reason               |
              | Plan                 |
              | Propose Action       |
              +----------------------+
                         |
                         v
              +----------------------+
              | Proposed Browser     |
              | Action               |
              +----------------------+
                         |
                         v
       +---------------------------------------+
       |         SECURITY ENFORCEMENT           |
       |                                       |
       |  GoalGuard: Goal Verification         |
       |  WebPermit: Permission Checking       |
       |  ActionShield: Action Enforcement    |
       |  LeakGuard: Data-Flow Protection      |
       |  SafeClick: Human Approval            |
       +---------------------------------------+
                         |
                         v
               Authorization Decision
                    /          \
                   v            v
                ALLOW          DENY
                   |            |
                   v            v
           Browser Execution  Block or Review
                   |            |
                   +------+-----+
                          |
                          v
               +----------------------+
               | Audit and Monitoring |
               +----------------------+
                          |
                          v
               +----------------------+
               | Evaluation           |
               |                      |
               | WebGuardBench        |
               | RedBlue Lab          |
               +----------------------+

            MemoryShield protects
            persistent agent state.
```

This diagram describes the intended architecture. Actual guarantees depend on implementation details, policy correctness, and browser interception coverage.

### Design Principles

- **Separation of reasoning and enforcement:** The model proposes actions; the security layer independently checks authorization.
- **Explicit authorization:** The user's task and permissions define the allowed scope of execution.
- **Pre-execution checks:** Security checks should occur before external effects whenever reliable interception is possible.
- **Defense in depth:** Different controls address different failure modes.
- **Auditability:** Security decisions should be recorded and explainable.
- **Measurable effectiveness:** Defenses must be evaluated for security, utility, and runtime cost.

---

# Research Directions

The repository supports several related research directions.

1. **Direct Prompt Injection:** Understand how adversarial instructions influence Web Agent decisions and execution.
2. **Goal Deviation:** Identify when an action or trajectory departs from the authorized objective.
3. **Runtime Enforcement:** Prevent unauthorized browser actions before they produce external effects.
4. **Least-Privilege Security:** Limit the capabilities available to an agent.
5. **Privacy Protection:** Prevent unauthorized sensitive data disclosure.
6. **Memory Security:** Protect persistent agent state from untrusted instructions.
7. **Security Evaluation:** Build reproducible tests for attacks and defenses.
8. **Security–Utility Trade-Offs:** Improve protection without unnecessarily degrading legitimate task completion.

Each research paper should focus on a well-defined problem, a defensible research gap, a clear threat model, and experimentally supported contributions.

These directions are research goals, not claims of established novelty.

---

# Evaluation Metrics

The evaluation framework will measure both security effectiveness and legitimate task utility.

| Metric | Purpose |
|---|---|
| Attack Success Rate (ASR) | Measures how often an attack achieves its predefined objective. |
| Unauthorized Action Rate (UAR) | Measures how frequently unauthorized actions are executed. |
| Legitimate Task Success Rate | Measures successful completion of benign tasks. |
| False Blocking Rate | Measures legitimate actions incorrectly blocked by a defense. |
| Detection Precision | Measures the accuracy of security-violation detections. |
| Detection Recall | Measures the proportion of actual violations detected. |
| Detection F1 | Summarizes precision and recall. |
| Runtime Overhead | Measures additional latency introduced by the defense. |
| Recovery Rate | Measures recovery from defined attack-induced deviations. |
| Sensitive Data Leakage Rate | Measures unauthorized disclosure in controlled privacy tests. |

Metric definitions, trial counts, and evaluation procedures must be documented for every experiment.

Attack success and unauthorized action are distinct outcomes and should not be treated as interchangeable.

## Experimental Studies

Where applicable, evaluations should include:

- Baseline comparisons.
- Security effectiveness tests.
- Legitimate task completion tests.
- Ablation studies.
- Robustness tests.
- Generalization to unseen scenarios.
- Runtime and resource measurements.

Results should include appropriate uncertainty estimates and limitations. Performance improvements should be reported only after the corresponding experiments have been conducted.

---

# Technology Stack

The initial development stack is expected to include:

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python | Core implementation |
| Browser automation | Playwright | Browser interaction |
| Agent orchestration | LangGraph or a custom agent loop | Agent execution |
| Evaluation environments | BrowserGym and compatible environments | Web task evaluation |
| Backend API | FastAPI | Optional service interfaces |
| Dashboard | Streamlit | Experimental visualization |
| Testing | pytest | Unit and integration testing |
| Configuration | YAML / JSON | Policies and experiment settings |
| Version control | Git | Source management |
| Repository hosting | GitHub | Collaboration and reproducibility |

Final dependencies and supported versions will be documented as implementations become available.

---

# Repository Structure

All projects will be maintained under one GitHub repository, with a dedicated directory for each project.

```text
advanced-web-agent-security/
│
├── projects/
│   ├── actionshield/
│   ├── webguardbench/
│   ├── goalguard/
│   ├── leakguard/
│   ├── safeclick/
│   ├── memoryshield/
│   ├── redblue-lab/
│   └── webpermit/
│
├── shared/
│   ├── agent_adapters/
│   ├── browser/
│   ├── policies/
│   ├── logging/
│   └── evaluation/
│
├── benchmarks/
│   ├── tasks/
│   ├── attacks/
│   ├── expected_outcomes/
│   └── results/
│
├── configs/
│   ├── agents/
│   ├── policies/
│   └── experiments/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
│
├── docs/
│   ├── architecture/
│   ├── threat_model/
│   ├── methodology/
│   └── experiments/
│
├── scripts/
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

This structure is a starting point. Directories and shared utilities should be introduced incrementally as the corresponding implementations are developed.

---

# Getting Started

## Prerequisites

The initial development environment is expected to require:

- Python 3.11 or another supported Python version.
- Git.
- Playwright and a compatible browser.
- An LLM endpoint or locally available model for agent experiments.
- An authorized test environment.

Exact requirements will be specified for each project.

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/advanced-web-agent-security.git

cd advanced-web-agent-security
```

Replace `YOUR_USERNAME` with the GitHub account or organization that owns the repository.

## 2. Create a Virtual Environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

After the root `requirements.txt` has been populated with the tested dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install the Browser

After Playwright has been added to the dependencies:

```bash
playwright install chromium
```

## 5. Run Tests

Once the test suite is available:

```bash
python -m pytest tests/ -v
```

These commands describe the intended setup workflow. They do not imply that every project or test suite is already implemented.

For project-specific installation instructions, refer to the corresponding project directory once its README is available.

---

# Development Roadmap

## Phase 1: Foundations

- [ ] Define the threat model and authorization boundaries.
- [ ] Establish the repository structure.
- [ ] Integrate a baseline Web Agent.
- [ ] Create controlled local websites and benign tasks.
- [ ] Record browser observations and action trajectories.

## Phase 2: Core Security

- [ ] Implement ActionShield.
- [ ] Develop the initial GoalGuard verifier.
- [ ] Implement WebPermit authorization policies.
- [ ] Add security decision logging.
- [ ] Test authorized and unauthorized actions.

## Phase 3: Security Evaluation

- [ ] Develop WebGuardBench task definitions.
- [ ] Establish ground-truth authorization labels.
- [ ] Implement evaluation metrics.
- [ ] Create controlled direct prompt-injection scenarios.
- [ ] Compare baseline and defended agents.

## Phase 4: Extended Protection

- [ ] Develop LeakGuard.
- [ ] Implement SafeClick.
- [ ] Investigate MemoryShield.
- [ ] Integrate RedBlue Lab.
- [ ] Test interactions between modules.

## Phase 5: Research and Reproducibility

- [ ] Conduct ablation studies.
- [ ] Evaluate robustness across attack conditions.
- [ ] Measure security–utility trade-offs.
- [ ] Evaluate generalization to unseen scenarios.
- [ ] Document reproducible experiment configurations.
- [ ] Publish validated findings and implementation limitations.

Progress should be tracked for each project independently. Features should be marked complete only after implementation and relevant testing.

---

# Security and Responsible Use

This repository is intended for authorized security research, defensive engineering, and controlled evaluation.

- Prefer local mock websites and synthetic accounts.
- Do not test against third-party services without authorization.
- Do not use real credentials or unnecessary personal information in experiments.
- Isolate adversarial scenarios from production systems.
- Use synthetic data for privacy and exfiltration testing.
- Document threat models and assumptions.
- Report false positives, false negatives, and known limitations.
- Avoid claims of complete protection based on limited experiments.

The effectiveness of a security mechanism depends on its implementation, policy correctness, threat model, and evaluation coverage.

---

# Reproducibility

Each completed experiment should document:

- Agent model and version.
- Browser and execution environment.
- Task and attack configurations.
- Defense settings and thresholds.
- Dataset and sampling procedure.
- Metric definitions.
- Random seeds where applicable.
- Number of evaluation trials.
- Raw or appropriately sanitized results.
- Statistical uncertainty and limitations.

Experiment configurations should be version-controlled so that results can be reproduced and compared.

Credentials, secrets, and private user information must not be included in published artifacts.

---

# Contributing

Contributions are welcome in:

- Web Agent security research.
- Direct prompt-injection evaluation.
- Runtime policy enforcement.
- Browser permission systems.
- Sensitive data protection.
- Memory security.
- Benchmark development.
- Testing and reproducibility.
- Documentation and engineering.

Before contributing a new project, document its security problem, threat model, technical approach, interfaces, evaluation plan, and relationship to existing modules.

---

# Research and Publications

This repository is intended to support research into trustworthy LLM-based Web Agents, direct prompt injection, runtime enforcement, and reproducible security evaluation.

Potential research topics include:

- Action-level security enforcement.
- Goal-conditioned verification of browser actions.
- Detection and measurement of goal deviation.
- Least-privilege defenses against direct prompt injection.
- Privacy-aware Web Agent execution.
- Persistent memory security.
- Security–utility trade-offs in autonomous Web Agents.

Publications, technical reports, and validated implementations will be linked here as they become available.

Research novelty should be established through a review of relevant prior work and supported by experimental evidence.

---

# Citation

Citation information will be added when a corresponding research paper or technical report is available.

Please cite the relevant underlying papers, models, benchmarks, datasets, and software libraries used in your work.

---

# License

Choose and add an appropriate open-source license before distributing the repository.

MIT and Apache-2.0 are possible options, depending on the project's reuse and patent-licensing requirements.

The licenses of third-party models, datasets, benchmarks, and dependencies must also be respected.

Until a license is selected and added, no particular open-source license should be assumed.

---

## Vision

**To develop practical, measurable, and reproducible security mechanisms that help LLM-based Web Agents remain within their authorized objectives, even when confronted with adversarial instructions.**

Advanced Web Agent Security brings multiple complementary projects together under one repository, providing a foundation for continued software development, rigorous security evaluation, and future research contributions.
