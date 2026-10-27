import asyncio
import importlib
import json
import os
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ..scenarios.schema import Action, Scenario


class ScriptedAgent:
    """A deterministic fixture, never presented as an evaluated language model."""

    def __init__(self, task_only=False):
        self.task_only = task_only
        self.metadata = {
            "name": "task-only" if task_only else "scripted",
            "version": "1",
            "scripted_fixture": True,
            "uses_ground_truth": task_only,
        }

    async def initialize(self, scenario: Scenario, seed: int) -> None:
        self.actions = iter(
            a for a in scenario.script if not self.task_only or scenario.authorized(a)
        )

    async def propose_action(self, observation: dict) -> Action | None:
        return next(self.actions, None)

    async def shutdown(self) -> None:
        pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class JsonEndpointAgent:
    """Provider-neutral HTTP contract for a separately hosted real agent/model."""

    def __init__(self):
        self.endpoint = os.environ.get("WGB_AGENT_ENDPOINT", "")
        parsed = urlsplit(self.endpoint)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "Set WGB_AGENT_ENDPOINT to an HTTP(S) URL without credentials or query"
            )
        self.token = os.environ.get("WGB_AGENT_TOKEN")
        if (
            self.token
            and parsed.scheme != "https"
            and parsed.hostname not in {"127.0.0.1", "localhost"}
        ):
            raise ValueError("Remote agent endpoints require HTTPS when using an access token")
        self.metadata = {
            "name": "json-endpoint",
            "version": "1",
            "endpoint_origin": f"{parsed.scheme}://{parsed.netloc}",
            "scripted_fixture": False,
            "model": os.environ.get("WGB_AGENT_MODEL", "unspecified"),
        }

    async def initialize(self, scenario: Scenario, seed: int) -> None:
        self.context = {
            "task": scenario.task.description,
            "direct_injection": scenario.attack.instruction if scenario.attack else None,
            "scenario_id": scenario.scenario_id,
            "seed": seed,
            "model": self.metadata["model"],
        }
        self.history = []

    def _request(self, observation):
        payload = json.dumps(
            {**self.context, "observation": observation, "history": self.history}
        ).encode()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(self.endpoint, payload, headers, method="POST")
        # Transport errors do not include request bodies, tokens or arbitrary server responses.
        try:
            # Do not forward authorization headers to a redirect destination.
            with build_opener(NoRedirect).open(request, timeout=20) as response:
                raw = response.read(1_048_577)
                if len(raw) > 1_048_576:
                    raise ValueError("Agent response exceeds 1 MiB")
                data = json.loads(raw)
        except Exception as exc:
            raise RuntimeError(f"Agent endpoint request failed ({type(exc).__name__})") from None
        if not isinstance(data, dict) or set(data) != {"action"}:
            raise ValueError("Agent endpoint must return exactly {'action': object or null}")
        return Action.from_dict(data["action"]) if data["action"] is not None else None

    async def propose_action(self, observation: dict) -> Action | None:
        action = await asyncio.to_thread(self._request, observation)
        self.history.append(
            {
                "action": None
                if action is None
                else {"kind": action.kind, "target": action.target},
                "previous_result": observation.get("previous_result"),
            }
        )
        return action

    async def shutdown(self) -> None:
        pass


def create_agent(name: str):
    if name in {"scripted", "task-only"}:
        return ScriptedAgent(task_only=name == "task-only")
    if name == "json-endpoint":
        return JsonEndpointAgent()
    if ":" in name:
        module, factory = name.split(":", 1)
        agent = getattr(importlib.import_module(module), factory)()
        for method in ("initialize", "propose_action", "shutdown"):
            if not callable(getattr(agent, method, None)):
                raise ValueError(f"Custom agent must implement {method}")
        return agent
    raise ValueError(f"Unknown agent: {name}")
