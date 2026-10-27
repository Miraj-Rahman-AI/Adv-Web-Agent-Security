import pytest

from webguardbench.scenarios.loader import load_scenarios


@pytest.fixture
def shopping():
    return next(s for s in load_scenarios() if s.scenario_id == "shopping_injection_001")
