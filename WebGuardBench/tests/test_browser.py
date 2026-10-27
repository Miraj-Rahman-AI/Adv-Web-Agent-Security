import asyncio
import importlib.util
import os

import pytest

from webguardbench.defenses import Defense
from webguardbench.environments.browser import BrowserEnvironment
from webguardbench.evaluator import evaluate_trajectory
from webguardbench.runner.experiment import run_experiment
from webguardbench.scenarios.loader import load_scenarios

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("WGB_TEST_BROWSER") != "1",
        reason="Set WGB_TEST_BROWSER=1 after installing Chromium",
    ),
]


@pytest.mark.parametrize("scenario", load_scenarios(), ids=lambda s: s.scenario_id)
@pytest.mark.parametrize("defense", ["none", "allowlist"])
def test_chromium_observed_effects_match_memory_backend(scenario, defense):
    async def compare():
        browser = await run_experiment(scenario, defense=Defense(defense), backend="browser")
        memory = await run_experiment(scenario, defense=Defense(defense))
        assert browser.status == "completed", browser.error
        assert browser.final_observation == memory.final_observation
        assert [s.effects for s in browser.steps] == [s.effects for s in memory.steps]
        a, b = evaluate_trajectory(scenario, browser), evaluate_trajectory(scenario, memory)
        for key in (
            "task_success",
            "attack_success",
            "unauthorized_executed",
            "recovered_episodes",
        ):
            assert a[key] == b[key]

    asyncio.run(compare())


def test_browser_blocks_requests_outside_fixture_origin(shopping):
    async def check():
        env = BrowserEnvironment()
        try:
            await env.start(shopping)
            outcome = await env.page.evaluate("""async () => {
                try { await fetch('http://127.0.0.1:1/outside'); return 'allowed'; }
                catch { return 'blocked'; }
            }""")
            assert outcome == "blocked"
            assert env.site.state.effects == set()
        finally:
            await env.close()

    asyncio.run(check())


@pytest.mark.skipif(
    importlib.util.find_spec("actionshield") is None, reason="ActionShield not on path"
)
def test_actionshield_intercepts_browser_purchase(shopping):
    raw = asyncio.run(run_experiment(shopping, defense=Defense("actionshield"), backend="browser"))
    result = evaluate_trajectory(shopping, raw)
    assert raw.status == "completed", raw.error
    assert result["task_success"] is True and result["attack_success"] is False
    assert raw.steps[1].executed is False
