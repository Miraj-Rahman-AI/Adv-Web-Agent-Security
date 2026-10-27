import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from webguardbench.agents.adapters import JsonEndpointAgent, create_agent
from webguardbench.evaluator import evaluate_trajectory
from webguardbench.runner.experiment import run_experiment


@pytest.fixture
def endpoint(monkeypatch):
    received = []
    actions = [
        {"kind": "read", "target": "laptop-a"},
        {"kind": "read", "target": "laptop-b"},
        {"kind": "compare"},
        {"kind": "report"},
        None,
    ]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            result = json.dumps({"action": actions.pop(0)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("WGB_AGENT_ENDPOINT", f"http://127.0.0.1:{server.server_port}/act")
    monkeypatch.setenv("WGB_AGENT_TOKEN", "synthetic-test-token")
    try:
        yield received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_agent_contract_runs_without_publishing_token(shopping, endpoint):
    raw = asyncio.run(run_experiment(shopping, agent_name="json-endpoint"))
    result = evaluate_trajectory(shopping, raw)
    assert raw.status == "completed"
    assert result["task_success"] is True and result["attack_success"] is False
    assert endpoint[0]["task"] == shopping.task.description
    assert endpoint[0]["direct_injection"] == shopping.attack.instruction
    assert endpoint[1]["history"]
    assert endpoint[1]["observation"]["previous_result"]["success"] is True
    assert "synthetic-test-token" not in json.dumps(raw.to_dict())


def test_custom_agent_factory_is_supported():
    assert create_agent("webguardbench.agents.adapters:ScriptedAgent").metadata["scripted_fixture"]
    with pytest.raises(ValueError, match="Unknown agent"):
        create_agent("absent")


@pytest.mark.parametrize(
    "url",
    ["", "file:///private", "https://user:pass@example.com/", "https://example.com/?token=private"],
)
def test_endpoint_rejects_invalid_or_secret_bearing_urls(monkeypatch, url):
    monkeypatch.setenv("WGB_AGENT_ENDPOINT", url)
    with pytest.raises(ValueError):
        JsonEndpointAgent()
