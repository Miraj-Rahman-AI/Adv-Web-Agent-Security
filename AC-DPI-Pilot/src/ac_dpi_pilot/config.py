import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from ac_dpi_pilot.paths import PROJECT_ROOT


load_dotenv(PROJECT_ROOT / ".env")


def parse_bool(value):
    return str(value).strip().lower() in {
        "1", "true", "yes", "on"
    }


def parse_models(value):
    return tuple(
        item.strip()
        for item in value.split(",")
        if item.strip()
    )


@dataclass(frozen=True)
class Settings:

    ollama_base_url: str

    default_model: str

    models: tuple

    temperature: float

    num_predict: int

    timeout: int

    seed: int

    repetitions: int

    results_dir: Path

    allow_insecure_remote: bool

    @classmethod
    def from_env(cls):

        settings = cls(

            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://127.0.0.1:11434"
            ).rstrip("/"),

            default_model=os.getenv(
                "OLLAMA_MODEL",
                "qwen3.5:4b"
            ),

            models=parse_models(
                os.getenv(
                    "OLLAMA_MODELS",
                    "qwen3.5:4b,gemma3:4b"
                )
            ),

            temperature=float(
                os.getenv("OLLAMA_TEMPERATURE", "0.0")
            ),

            num_predict=int(
                os.getenv("OLLAMA_NUM_PREDICT", "384")
            ),

            timeout=int(
                os.getenv("OLLAMA_TIMEOUT", "240")
            ),

            seed=int(
                os.getenv("AC_DPI_SEED", "42")
            ),

            repetitions=int(
                os.getenv("AC_DPI_REPETITIONS", "10")
            ),

            results_dir=Path(
                os.getenv("AC_DPI_RESULTS_DIR", "results")
            ),

            allow_insecure_remote=parse_bool(
                os.getenv(
                    "AC_DPI_ALLOW_INSECURE_REMOTE",
                    "false"
                )
            )
        )

        settings.validate()

        return settings

    def validate(self):

        parsed = urlparse(self.ollama_base_url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("OLLAMA_BASE_URL must use HTTP or HTTPS.")

        if not parsed.hostname:
            raise ValueError("OLLAMA_BASE_URL must contain a hostname.")

        if parsed.username or parsed.password:
            raise ValueError("Do not embed credentials in the service URL.")

        if parsed.query or parsed.fragment:
            raise ValueError("Service URL must not contain query or fragment.")

        hostname = parsed.hostname.lower()

        local_hosts = {
            "localhost",
            "127.0.0.1",
            "::1"
        }

        if (
            parsed.scheme == "http"
            and hostname not in local_hosts
            and not self.allow_insecure_remote
        ):
            raise ValueError(
                "Remote HTTP is disabled. Use HTTPS or explicitly "
                "enable AC_DPI_ALLOW_INSECURE_REMOTE."
            )

        if not self.default_model:
            raise ValueError("Default model cannot be empty.")

        if not self.models:
            raise ValueError("At least one evaluation model is required.")

        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2.")

        if self.num_predict < 1:
            raise ValueError("num_predict must be positive.")

        if self.timeout < 1:
            raise ValueError("Timeout must be positive.")

        if self.repetitions < 1:
            raise ValueError("Repetitions must be positive.")


settings = Settings.from_env()
