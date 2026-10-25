import json
import logging
import threading

from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from .models import ActionRequest
from .policy import hostname_for_url


class AuditSink(Protocol):
    def record(
        self,
        request: ActionRequest,
        status: str,
        reason: str,
    ) -> None:
        ...


def make_event(
    request: ActionRequest,
    status: str,
    reason: str,
) -> dict:
    """Create an audit event without recording raw form data."""

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request.request_id,
        "action_type": request.action_type.value,
        "current_host": hostname_for_url(request.current_url),
        "destination_host": hostname_for_url(
            request.destination_url
        ),
        "impact": request.impact.value,
        "status": status,
        "reason": reason,
    }


class LoggingAuditSink:
    """Send structured audit events to Python logging."""

    def record(self, request, status, reason):
        event = make_event(request, status, reason)

        logging.getLogger("actionshield.audit").info(
            "%s",
            json.dumps(event),
        )


class JsonlAuditLogger:
    """Append structured audit events to a JSONL file."""

    def __init__(self, path: str = "logs/actionshield.jsonl"):
        self.path = Path(path)
        self._lock = threading.Lock()

    def record(self, request, status, reason):
        event = make_event(request, status, reason)

        with self._lock:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.path.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(json.dumps(event) + "\n")


class InMemoryAuditLogger:
    """Useful for tests and development."""

    def __init__(self):
        self.events: list[dict] = []

    def record(self, request, status, reason):
        self.events.append(
            make_event(request, status, reason)
        )
