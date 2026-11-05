from pathlib import Path
from datetime import datetime, timezone


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCS_DIR = PROJECT_ROOT / "docs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
TESTS_DIR = PROJECT_ROOT / "tests"
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

RESULTS_DIR = PROJECT_ROOT / "results"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"
SUMMARY_RESULTS_DIR = RESULTS_DIR / "summaries"


def ensure_result_directories():
    """Create experimental result directories when needed."""

    RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def create_run_id(prefix="run"):
    """Generate a UTC-based experiment identifier."""

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    return f"{prefix}_{timestamp}"


def get_result_path(filename, raw=False):
    """Return a path inside the correct results directory."""

    ensure_result_directories()

    directory = RAW_RESULTS_DIR if raw else SUMMARY_RESULTS_DIR

    return directory / filename


def project_relative(path):
    """Convert an absolute path into a project-relative path."""

    return Path(path).resolve().relative_to(PROJECT_ROOT)
