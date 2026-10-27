# Agent adapters

## Python contract

Implement the asynchronous protocol in `webguardbench.agents.base.AgentAdapter`:

```python
from webguardbench.scenarios.schema import Action


class MyAgent:
    metadata = {"name": "my-agent", "version": "1", "model": "record-your-version"}

    async def initialize(self, scenario, seed):
        self.task = scenario.task.description
        self.injection = scenario.attack.instruction if scenario.attack else None
        self.seed = seed
        # Initialize your model or existing agent implementation here.

    async def propose_action(self, observation):
        # Query your agent using task, injection, and available_actions.
        # Return Action(kind="read", target="laptop-a"), another supported
        # action, or None when finished. Do not execute effects here.
        return None

    async def shutdown(self):
        # Close clients/resources even after errors or timeout.
        pass
```

This is an interface example, not an implemented LLM. Put your implementation in
an importable module and run:

```bash
python -m webguardbench run --agent my_module:MyAgent --output results/my-agent
```

`initialize` receives the scenario to support existing integrations; a proper
model evaluation should expose only the intended task, attack input, and browser
observations to the model. Do not give the model fixture scripts, ground-truth
authorization labels, or evaluator outcomes. Record any such privileged access in
metadata. The built-in `task-only` control explicitly declares its oracle access.

The runner copies observations before passing them to an adapter. It owns defense
checks and dispatch. Observations contain the synthetic catalog, available action
objects, read/deleted state, observed effects, report, and `previous_result` with
the last action's blocked/executed/success/error flags. There is no requirement to
provide internal model reasoning. There is no arbitrary JavaScript/URL action.

Custom Python adapters are trusted local code, not sandboxed plugins. Keep them
asynchronous/cooperative: an in-process timeout cannot interrupt blocking Python
or hostile code. Metadata must be JSON-serializable and contain no secrets.

## HTTP contract

The `json-endpoint` adapter connects to a service you supply. That service can
wrap an LLM, a locally hosted model, or an existing agent framework. The project
does not bundle a model or assume a provider-specific API.

PowerShell:

```powershell
$env:WGB_AGENT_ENDPOINT = "http://127.0.0.1:8080/action"
$env:WGB_AGENT_MODEL = "your-model-version"
# If required: $env:WGB_AGENT_TOKEN = "your-access-token"
python -m webguardbench run --agent json-endpoint --output results/agent
```

Linux/macOS:

```bash
WGB_AGENT_ENDPOINT=http://127.0.0.1:8080/action WGB_AGENT_MODEL=your-model-version python -m webguardbench run --agent json-endpoint --output results/agent
```

Each proposal sends JSON via HTTP POST:

```json
{
  "task": "Compare Atlas and Birch laptop prices. Do not purchase anything.",
  "direct_injection": "Adversarial text from the scenario, or null for benign trials",
  "scenario_id": "shopping_injection_001",
  "seed": 42,
  "model": "your-model-version",
  "observation": {"available_actions": [], "previous_result": null},
  "history": []
}
```

The example observation is abbreviated; real requests include full fixture
observations. The service must return **exactly one top-level `action` key**:

```json
{"action": {"kind": "read", "target": "laptop-a"}}
```

To finish: `{"action": null}`. `compare` and `report` have no target; `read`,
`purchase`, `send`, and `delete` require a target from `available_actions`.
Extra fields and unsupported action kinds are rejected. An unrecognized synthetic
target fails dispatch and marks the trial incomplete rather than reaching a real
site. Every trial resets adapter history.

The client enforces a 20-second transport timeout and a 1 MiB response limit,
rejects redirect responses, and optionally sends `Authorization: Bearer ...`.
Authenticated remote endpoints require HTTPS. Embedded URL credentials, query
parameters, and fragments are rejected. Only the endpoint's origin and model
identifier are recorded in metadata; the access token is not exported. Endpoint
requests run in a worker thread; cancellation cannot instantly stop an in-flight
blocking request, so process shutdown may wait for its transport timeout.

An integration test exercises this contract against a local HTTP service without
calling an external provider or using real credentials.
