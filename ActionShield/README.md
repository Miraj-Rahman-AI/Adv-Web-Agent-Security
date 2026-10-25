# ActionShield

**Runtime Security and Action Enforcement for LLM-Based Web Agents**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Browser](https://img.shields.io/badge/Browser-Playwright-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/)
[![Focus](https://img.shields.io/badge/Focus-AI%20Security-red)](../../README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Status](https://img.shields.io/badge/Status-Research%20%26%20Development-orange)](#project-status)

ActionShield is a runtime security component designed to control which actions an LLM-based Web Agent may execute.

It introduces an authorization layer between the agent's proposed actions and the operations performed by a browser. Before an action is executed through the protected interface, ActionShield evaluates the action against configured security policies, validates relevant URLs, and determines whether explicit human approval is required.

The project aims to reduce unauthorized browser actions caused by direct prompt injection, goal hijacking, excessive agency, and other agent decision failures.

> **Core principle:** An LLM-based agent may propose an action, but the security layer independently determines whether that action is authorized.

**Parent repository:** [Advanced Web Agent Security](../../README.md)

**Project status:** Research and development. The current implementation provides a basic policy engine, execution gating, approval callbacks, structured audit logging, a Playwright wrapper, and initial unit tests.

---

## Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [Objectives](#objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Execution Workflow](#execution-workflow)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Playwright Integration](#playwright-integration)
- [Audit Logging](#audit-logging)
- [Testing](#testing)
- [Security Considerations](#security-considerations)
- [Current Limitations](#current-limitations)
- [Development Roadmap](#development-roadmap)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

LLM-based Web Agents combine language models, browser observations, planning, and tool execution to complete tasks on websites.

However, an agent's ability to interact with websites introduces security risks. An adversarial instruction may cause the agent to navigate to an unauthorized website, submit a form, download a file, or attempt another action that falls outside the user's intended objective.

ActionShield addresses this problem by separating action proposal from action authorization.

Instead of allowing an agent to execute every proposed operation directly, ActionShield evaluates the operation against an explicit security policy before running the associated callback.

### Example scenario

Suppose a user asks an agent to compare three laptops without purchasing anything.

A webpage contains an adversarial instruction telling the agent to purchase one of the laptops immediately.

Without an appropriate enforcement mechanism, the agent might follow that instruction and attempt to make a purchase.

With ActionShield, a purchase-related operation can be classified as a sensitive action and blocked unless the configured policy and approval workflow authorize it.

The goal is to protect the user's authorization boundaries without unnecessarily preventing legitimate browsing.

## Motivation

Web Agent security requires more than checking whether an LLM generates an appropriate response. It also requires controlling the external actions that the agent can perform.

Important security challenges include:

- **Direct prompt injection:** Adversarial instructions attempt to redirect the agent.
- **Goal hijacking:** The agent departs from the user's original task.
- **Unauthorized actions:** The agent performs operations outside its granted permissions.
- **Excessive agency:** The agent has more capabilities than its task requires.
- **Sensitive operations:** An action may purchase an item, submit information, send a message, or modify data.
- **Insufficient auditability:** Security failures may be difficult to investigate without structured records of authorization decisions.

ActionShield focuses primarily on the action execution boundary. It does not assume that the underlying language model will always identify malicious instructions correctly.

---

## Objectives

The project's objectives are to:

1. Enforce explicit policies for supported browser actions.
2. Validate current and destination URLs against configured domain rules.
3. Deny actions that violate the configured policy.
4. Require explicit approval for selected sensitive actions.
5. Separate authorization decisions from action execution.
6. Record security decisions and execution outcomes.
7. Integrate with browser automation through a guarded interface.
8. Provide a foundation for evaluating runtime security mechanisms.

These objectives describe the intended direction of the project. Actual security guarantees depend on implementation coverage and testing.

---

## Features

| Feature | Description |
|---|---|
| Policy engine | Evaluates proposed actions against configured rules. |
| Domain allowlisting | Restricts supported operations to explicitly permitted domains. |
| Domain blocking | Explicitly denies configured domains and their subdomains. |
| Action authorization | Controls which action types may be executed. |
| Approval workflow | Requests approval for selected sensitive actions. |
| Execution gating | Prevents the supplied callback from executing when authorization fails. |
| Audit logging | Records decisions and execution outcomes in structured form. |
| Playwright wrapper | Provides guarded methods for selected browser operations. |
| Unit testing | Tests basic authorization and execution behavior. |

### Supported action types

The current data model defines the following action types:

- `NAVIGATE`
- `CLICK`
- `TYPE`
- `SUBMIT`
- `DOWNLOAD`
- `PURCHASE`
- `DELETE`
- `SEND`
- `MODIFY`

Defining an action type does not mean that every type already has a dedicated browser integration. For example, the initial Playwright wrapper does not implement dedicated `PURCHASE`, `DELETE`, or `SEND` methods.

---

## Architecture

ActionShield places a security enforcement layer between the agent's proposed action and its execution callback.

```text
                USER-AUTHORIZED TASK
                          |
                          v
                 +------------------+
                 |  LLM-Based Agent |
                 |                  |
                 | Observe          |
                 | Reason           |
                 | Plan             |
                 +------------------+
                          |
                          v
                 +------------------+
                 | Proposed Action  |
                 +------------------+
                          |
                          v
                 +------------------+
                 | ActionShield     |
                 |                  |
                 | Action Validation|
                 | Domain Policy    |
                 | Approval Rules   |
                 +------------------+
                          |
                          v
                 Authorization Decision
                     /          \
                    /            \
                   v              v
                ALLOW            DENY
                  |                |
                  v                v
          Execute Callback    Block Callback
                  |                |
                  +-------+--------+
                          |
                          v
                 +------------------+
                 | Audit Logging    |
                 |                  |
                 | Decision         |
                 | Execution Result |
                 +------------------+
```

### Main components

**1. Security data models**

`models.py` defines action requests, impact levels, decisions, and execution results.

**2. Policy engine**

`policy.py` validates URL domains and provides configurable rules for allowed actions, blocked domains, and approval requirements.

**3. Execution engine**

`engine.py` evaluates requests, enforces approval requirements, executes authorized callbacks, and records outcomes.

**4. Audit logger**

`audit.py` provides logging implementations for structured events, JSONL files, and in-memory tests.

**5. Browser integration**

`playwright_guard.py` wraps selected Playwright operations and provides a navigation interception mechanism.

**6. Tests and examples**

The test suite checks basic authorization behavior, while the demonstration illustrates how a sensitive operation can require approval.

---

## Execution Workflow

ActionShield follows this sequence:

1. **Receive an action request.** The agent or integration describes the proposed operation.
2. **Validate the action type.** Check whether the action is permitted by the configured policy.
3. **Validate URL context.** Check the current page and any known destination against the domain rules.
4. **Evaluate approval requirements.** Determine whether the action type or declared impact requires approval.
5. **Authorize or deny.** Block the callback if the policy rejects the action or approval is unavailable or denied.
6. **Execute the authorized callback.** Run the supplied operation only after the checks pass.
7. **Record the outcome.** Write a structured audit event.

An approval callback is an integration point, not an independent guarantee of user consent. A production system should connect it to a trustworthy approval interface and bind the approval to the specific action being authorized.

---

## Project Structure

```text
actionshield/
│
├── actionshield/
│   ├── __init__.py
│   ├── models.py
│   ├── policy.py
│   ├── audit.py
│   ├── engine.py
│   └── playwright_guard.py
│
├── tests/
│   └── test_engine.py
│
├── examples/
│   └── demo.py
│
├── requirements.txt
└── README.md
```

This structure represents the initial implementation.

---

## Requirements

The initial implementation uses:

- Python 3.11 or later.
- Playwright for browser integration.
- pytest for automated testing.

The policy engine and basic execution engine primarily use Python's standard library.

Exact dependency versions should be pinned and tested before production deployment.

## Installation

### 1. Navigate to the project

From the root of the parent repository:

```bash
cd projects/actionshield
```

### 2. Create a virtual environment

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

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install the Playwright browser

```bash
playwright install chromium
```

Browser installation is needed for browser integration tests and examples that use Chromium.

---

## Quick Start

The following example demonstrates the policy engine without opening a real website.

```python
import asyncio

from actionshield import (
    ActionImpact,
    ActionPolicy,
    ActionRequest,
    ActionShield,
    ActionType,
)
from actionshield.audit import InMemoryAuditLogger


async def main():
    policy = ActionPolicy(
        policy_id="example-policy",
        allowed_domains=frozenset({
            "example.com",
        }),
        allow_subdomains=False,
    )

    audit = InMemoryAuditLogger()

    shield = ActionShield(
        policy=policy,
        audit=audit,
    )

    request = ActionRequest(
        action_type=ActionType.SUBMIT,
        current_url="https://example.com/checkout",
        description="Submit a checkout form",
        impact=ActionImpact.HIGH,
    )

    async def approve_action(action, decision):
        print("Approval required:", decision.reason)

        # Demonstration only.
        # Replace with an explicit, trusted approval workflow.
        return False

    async def simulated_action():
        print("The operation is executing.")
        return {"status": "success"}

    result = await shield.execute(
        request=request,
        action=simulated_action,
        approval_callback=approve_action,
    )

    print("Executed:", result.executed)
    print("Decision:", result.decision.status.value)
    print("Reason:", result.decision.reason)


if __name__ == "__main__":
    asyncio.run(main())
```

Because the example approval callback returns `False`, the simulated operation is not executed.

A successful execution requires both a policy-permitted action and any required approval.

### Expected behavior

- An unlisted domain is denied.
- A blocked domain is denied.
- A supported action on an allowed domain may be permitted.
- A sensitive action requires approval.
- An approval rejection prevents the supplied callback from executing.
- An authorized operation is recorded in the audit log.

---

## Configuration

ActionShield uses `ActionPolicy` to define authorization rules.

```python
from actionshield import ActionPolicy, ActionType
from actionshield.models import ActionImpact

policy = ActionPolicy(
    policy_id="research-browser-v1",

    allowed_domains=frozenset({
        "example.com",
    }),

    blocked_domains=frozenset({
        "malicious.example",
    }),

    allowed_actions=frozenset({
        ActionType.NAVIGATE,
        ActionType.CLICK,
        ActionType.TYPE,
        ActionType.SUBMIT,
        ActionType.DOWNLOAD,
    }),

    require_approval_for=frozenset({
        ActionType.SUBMIT,
        ActionType.DOWNLOAD,
        ActionType.PURCHASE,
        ActionType.DELETE,
        ActionType.SEND,
        ActionType.MODIFY,
    }),

    require_approval_for_impact=frozenset({
        ActionImpact.HIGH,
        ActionImpact.CRITICAL,
    }),

    allow_subdomains=False,
)
```

### Policy behavior

**Allowed domains**

The agent's supported actions must operate within the configured domain allowlist.

**Blocked domains**

Explicitly blocked domains take precedence over the allowlist.

**Subdomains**

When `allow_subdomains=False`, `example.com` does not automatically authorize `shop.example.com`.

**Action types**

Only action types listed in `allowed_actions` pass the action-type check.

**Approval requirements**

Actions that match `require_approval_for` or `require_approval_for_impact` require an approval callback that returns approval.

### URL validation

The initial policy engine accepts absolute HTTP and HTTPS URLs and rejects unsupported schemes and URLs containing embedded credentials.

For example:

| URL | Expected result |
|---|---|
| `https://example.com/` | Allowed by the domain rule |
| `https://example.com/products` | Allowed by the domain rule |
| `https://shop.example.com/` | Denied by default |
| `https://malicious.example/` | Denied |
| `file:///etc/passwd` | Denied |
| `https://example.com@malicious.example/` | Denied |

These outcomes assume the example policy above and do not represent a guarantee that every operation on an allowed domain is safe.

---

## Playwright Integration

The `GuardedPage` wrapper in `playwright_guard.py` provides guarded methods for selected browser operations.

Its interface includes:

- `goto()` for navigation.
- `click()` for clicking an element.
- `fill()` for entering text into a form field.
- `submit()` for a sensitive form-submission operation.
- `download()` for requesting a file download.
- `install_navigation_guard()` for intercepting supported navigation requests.

### Integration principle

The agent should receive a restricted browser interface rather than unrestricted access to the underlying Playwright page.

For example, a protected application can initialize the wrapper as follows:

```python
from actionshield import ActionPolicy, ActionShield
from actionshield.playwright_guard import GuardedPage


policy = ActionPolicy(
    policy_id="browser-policy",
    allowed_domains=frozenset({
        "example.com",
    }),
)

shield = ActionShield(policy=policy)

# `page` must be a Playwright Page created by your
# browser integration.
guarded_page = GuardedPage(
    page=page,
    shield=shield,
)

await guarded_page.install_navigation_guard()

await guarded_page.goto(
    "https://example.com/"
)
```

The `page` variable is supplied by the surrounding Playwright setup; this snippet is not a complete standalone browser script.

### Integration limitations

The current wrapper mediates only the operations exposed through it. It does not automatically secure every browser capability.

In particular:

- The agent must not retain unrestricted access to the raw page or browser context.
- Popups and newly created pages require separate security handling.
- Downloads, form submissions, and other sensitive effects need dedicated integration tests.
- A click's true impact cannot always be inferred from its selector.
- A domain allowlist does not prove that a website or action is trustworthy.
- Browser actions outside the wrapper may bypass its policy checks.

Comprehensive browser-context mediation and explicit action-specific authorization are necessary before treating the integration as a production security boundary.

---

## Audit Logging

ActionShield supports structured audit events through the interfaces in `audit.py`.

Available implementations include:

- `LoggingAuditSink` for Python logging.
- `JsonlAuditLogger` for JSON Lines audit records.
- `InMemoryAuditLogger` for testing.

### Example

```python
from actionshield.audit import JsonlAuditLogger

audit = JsonlAuditLogger(
    "logs/actionshield-audit.jsonl"
)
```

An event records fields such as:

- Timestamp.
- Request identifier.
- Action type.
- Current hostname.
- Destination hostname, when available.
- Declared impact.
- Authorization or execution status.
- Decision reason.

The logger deliberately avoids storing raw form contents.

Audit logs may still reveal sensitive browsing metadata. Production deployments should apply appropriate access controls, retention policies, and log integrity protections.

---

## Testing

Run the unit tests from the ActionShield project directory:

```bash
python -m pytest tests/ -v
```

The initial test suite covers:

- Blocking unlisted domains.
- Rejecting subdomains by default.
- Allowing authorized navigation.
- Requiring approval for sensitive actions.
- Preventing execution after approval rejection.
- Executing an approved operation.
- Rejecting unsupported URLs.

The initial unit tests do not comprehensively test browser interception or real-world prompt-injection resistance.

Additional integration tests should cover redirects, popups, downloads, form submissions, concurrent actions, and attempts to bypass the guarded interface.

---

## Security Considerations

ActionShield is a defensive security component, not a complete solution to Web Agent security.

### Fail-closed behavior

An empty domain allowlist does not authorize every website. Unsupported URL schemes and invalid URL contexts are rejected by the policy engine.

### Independent enforcement

The authorization decision should not be delegated solely to the LLM being protected.

### Human approval

Approval should be explicit, understandable, and bound to the exact action being approved. A generic approval response should not authorize unrelated future actions.

### Sensitive data

Avoid recording passwords, authentication tokens, private form values, or other sensitive data in audit logs.

### Defense in depth

ActionShield should be combined with complementary controls such as goal verification, least-privilege permissions, data-flow monitoring, and execution auditing.

---

## Current Limitations

The current implementation is an initial research prototype.

Known limitations include:

1. **Incomplete browser coverage:** Only selected operations are exposed through the wrapper.
2. **Declared impact:** Risk classification depends on the caller supplying an appropriate impact level.
3. **Limited authorization semantics:** Domain and action-type rules do not fully represent user intent.
4. **Approval integration:** A trusted human approval interface has not been implemented.
5. **No standalone prompt-injection detector:** ActionShield does not independently determine whether arbitrary text is malicious.
6. **Incomplete browser isolation:** Other browser contexts, popups, and direct tool access need additional enforcement.
7. **Limited evaluation:** The initial tests validate basic behavior, not comprehensive real-world security.
8. **Concurrency and state:** More work is needed to bind approvals to browser state and prevent time-of-check/time-of-use problems.

These limitations should be addressed and evaluated before production deployment.

---

## Development Roadmap

### Phase 1: Core Engine

- [x] Define action and decision data models.
- [x] Implement basic domain and action policies.
- [x] Implement callback execution gating.
- [x] Add approval callbacks.
- [x] Add structured audit logging.
- [x] Write initial unit tests.

### Phase 2: Browser Enforcement

- [x] Implement an initial Playwright wrapper.
- [x] Add a navigation interception mechanism.
- [ ] Mediate all relevant browser actions.
- [ ] Handle popups and newly created pages.
- [ ] Improve download and submission enforcement.
- [ ] Add comprehensive browser integration tests.

### Phase 3: Authorization Improvements

- [ ] Bind approvals to specific actions and browser states.
- [ ] Add stronger action schemas and validation.
- [ ] Integrate explicit task authorization.
- [ ] Integrate with GoalGuard.
- [ ] Integrate with WebPermit.
- [ ] Add security regression tests.

### Phase 4: Research Evaluation

- [ ] Define a reproducible Web Agent security test suite.
- [ ] Measure unauthorized action rates.
- [ ] Evaluate legitimate task completion.
- [ ] Measure false blocking and runtime overhead.
- [ ] Test prompt-injection scenarios in controlled environments.
- [ ] Document limitations and experimental findings.

Roadmap checkboxes describe the initial code and planned work. Browser-level guarantees and research outcomes must be established through further implementation and testing.

---

## Related Projects

ActionShield is part of the [Advanced Web Agent Security](../../README.md) project collection.

Related modules include:

- **GoalGuard:** Goal-conditioned verification of proposed actions.
- **WebPermit:** Least-privilege browser and tool authorization.
- **AgentFirewall:** Instruction-conflict and prompt-injection analysis.
- **AgentSentinel:** Runtime monitoring and security auditing.
- **WebGuardBench:** Reproducible security benchmarking.
- **LeakGuard:** Sensitive data exfiltration prevention.
- **SafeClick:** Risk-aware human approval.
- **MemoryShield:** Persistent agent memory security.
- **RedBlue Lab:** Controlled attack-defense evaluation.

These modules have complementary intended responsibilities and should not be treated as implemented integrations until those integrations exist and have been tested.

---

## Contributing

Contributions are welcome in:

- Runtime action enforcement.
- Browser automation security.
- Authorization policy design.
- Prompt-injection defense.
- Security auditability.
- Automated testing.
- Benchmark development.
- Documentation and reproducibility.

Contributions should include clear assumptions, tests for relevant security properties, and documentation of known limitations.

## License

ActionShield is distributed under the **MIT License**.

See the [parent repository's LICENSE file](../../LICENSE) for the full license text.

Copyright and licensing obligations for third-party dependencies remain applicable.

---

## Project Status

ActionShield is an evolving research and engineering project. Its initial implementation establishes a foundation for policy-based action enforcement, approval workflows, audit logging, and guarded browser operations.

The long-term objective is to investigate how runtime enforcement can help LLM-based Web Agents execute user-authorized tasks while reducing unauthorized actions, including those induced by direct prompt injection.

**An agent may propose an action. ActionShield checks whether it is authorized to execute it.**
