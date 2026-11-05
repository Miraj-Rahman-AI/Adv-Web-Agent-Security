import pytest

from pathlib import Path

from ac_dpi_pilot.config import (
    Settings,
    parse_bool,
    parse_models
)


def valid_settings():

    return Settings(

        ollama_base_url="http://127.0.0.1:11434",

        default_model="qwen3.5:4b",

        models=("qwen3.5:4b", "gemma3:4b"),

        temperature=0.0,

        num_predict=384,

        timeout=240,

        seed=42,

        repetitions=10,

        results_dir=Path("results"),

        allow_insecure_remote=False
    )


def test_valid_configuration():

    config = valid_settings()

    config.validate()


def test_boolean_parsing():

    assert parse_bool("true")
    assert parse_bool("YES")
    assert parse_bool("1")

    assert not parse_bool("false")
    assert not parse_bool("0")


def test_model_parsing():

    result = parse_models(
        "qwen3.5:4b, gemma3:4b"
    )

    assert result == (
        "qwen3.5:4b",
        "gemma3:4b"
    )


def test_invalid_temperature():

    config = valid_settings()

    config = Settings(
        **{
            **config.__dict__,
            "temperature": 3.0
        }
    )

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_remote_http():

    config = valid_settings()

    config = Settings(
        **{
            **config.__dict__,
            "ollama_base_url": "http://example.com:11434",
            "allow_insecure_remote": False
        }
    )

    with pytest.raises(ValueError):
        config.validate()


def test_remote_https_allowed():

    config = valid_settings()

    config = Settings(
        **{
            **config.__dict__,
            "ollama_base_url": "https://example.com:11434"
        }
    )

    config.validate()
