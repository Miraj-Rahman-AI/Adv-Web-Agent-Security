import json
from importlib.resources import files
from pathlib import Path

import yaml

from .schema import Scenario, scenario_from_dict


class UniqueKeyLoader(yaml.SafeLoader):
    """Do not silently let a second YAML key replace an authorization rule."""


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"YAML mapping has a duplicate or non-string key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_document(path: str | Path) -> dict:
    path = Path(path)
    content = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        return json.loads(content, object_pairs_hook=_json_pairs)
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError("Configuration must be JSON or YAML")
    return yaml.load(content, Loader=UniqueKeyLoader)


def load_scenario(path: str | Path) -> Scenario:
    return scenario_from_dict(load_document(path))


def load_scenarios(path: str | Path | None = None) -> list[Scenario]:
    if path is None:
        resources = files("webguardbench").joinpath("data", "scenarios")
        scenarios = [
            scenario_from_dict(yaml.load(p.read_text(encoding="utf-8"), Loader=UniqueKeyLoader))
            for p in sorted(resources.iterdir(), key=lambda p: p.name)
            if p.name.endswith(".yaml")
        ]
    else:
        source = Path(path)
        paths = (
            sorted(p for p in source.iterdir() if p.suffix.lower() in {".yaml", ".yml", ".json"})
            if source.is_dir()
            else [source]
        )
        scenarios = [load_scenario(p) for p in paths]
    if not scenarios:
        raise ValueError("No scenarios found")
    ids = [s.scenario_id for s in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("Scenario IDs must be unique")
    return scenarios
