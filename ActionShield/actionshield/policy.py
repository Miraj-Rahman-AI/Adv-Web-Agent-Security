from dataclasses import dataclass, field
from urllib.parse import urlsplit

from .models import ActionImpact, ActionType


def normalize_domain(domain: str) -> str:
    """Normalize a bare hostname used in a policy."""

    if not isinstance(domain, str):
        raise ValueError("Domain must be a string.")

    domain = domain.strip().rstrip(".").lower()

    if not domain:
        raise ValueError("Domain cannot be empty.")

    if any(char in domain for char in "/:@?#"):
        raise ValueError(
            "Use a bare hostname, not a URL or hostname with a port."
        )

    try:
        return domain.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("Invalid domain name.") from exc


def hostname_for_url(url: str | None) -> str | None:
    """Return a normalized hostname for an HTTP(S) URL."""

    if not url:
        return None

    try:
        parsed = urlsplit(url)

        if parsed.scheme.lower() not in {"http", "https"}:
            return None

        # Reject URLs containing embedded credentials.
        if parsed.username is not None or parsed.password is not None:
            return None

        if not parsed.hostname:
            return None

        return normalize_domain(parsed.hostname)

    except (ValueError, UnicodeError):
        return None


def domain_matches(
    hostname: str,
    rule: str,
    include_subdomains: bool,
) -> bool:
    """Match an exact hostname or an explicitly permitted subdomain."""

    if hostname == rule:
        return True

    return (
        include_subdomains
        and hostname.endswith("." + rule)
    )


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    """Authorization rules applied to proposed agent actions."""

    policy_id: str = "default"

    allowed_domains: frozenset[str] = field(
        default_factory=frozenset
    )

    blocked_domains: frozenset[str] = field(
        default_factory=frozenset
    )

    allowed_actions: frozenset[ActionType] = field(
        default_factory=lambda: frozenset(ActionType)
    )

    require_approval_for: frozenset[ActionType] = field(
        default_factory=lambda: frozenset({
            ActionType.SUBMIT,
            ActionType.DOWNLOAD,
            ActionType.PURCHASE,
            ActionType.DELETE,
            ActionType.SEND,
            ActionType.MODIFY,
        })
    )

    require_approval_for_impact: frozenset[ActionImpact] = field(
        default_factory=lambda: frozenset({
            ActionImpact.HIGH,
            ActionImpact.CRITICAL,
        })
    )

    allow_subdomains: bool = False

    def __post_init__(self):
        object.__setattr__(
            self,
            "allowed_domains",
            frozenset(
                normalize_domain(d)
                for d in self.allowed_domains
            ),
        )

        object.__setattr__(
            self,
            "blocked_domains",
            frozenset(
                normalize_domain(d)
                for d in self.blocked_domains
            ),
        )

        object.__setattr__(
            self,
            "allowed_actions",
            frozenset(ActionType(a) for a in self.allowed_actions),
        )

        object.__setattr__(
            self,
            "require_approval_for",
            frozenset(
                ActionType(a) for a in self.require_approval_for
            ),
        )

        object.__setattr__(
            self,
            "require_approval_for_impact",
            frozenset(
                ActionImpact(a)
                for a in self.require_approval_for_impact
            ),
        )

        if not self.policy_id.strip():
            raise ValueError("policy_id cannot be empty.")

    def url_error(self, url: str | None) -> str | None:
        """Return an explanation if a URL violates domain policy."""

        hostname = hostname_for_url(url)

        if hostname is None:
            return (
                "Invalid or unsupported URL. "
                "An absolute HTTP(S) URL is required."
            )

        # Explicit denials take precedence over allowlisting.
        if any(
            domain_matches(hostname, blocked, True)
            for blocked in self.blocked_domains
        ):
            return f"Host '{hostname}' is explicitly blocked."

        # An empty allowlist never means allow all.
        if not self.allowed_domains:
            return "No allowed domains are configured."

        if not any(
            domain_matches(
                hostname,
                allowed,
                self.allow_subdomains,
            )
            for allowed in self.allowed_domains
        ):
            return f"Host '{hostname}' is not in the allowlist."

        return None
