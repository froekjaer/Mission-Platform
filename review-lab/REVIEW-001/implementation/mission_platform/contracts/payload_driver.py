"""
contracts.payload_driver — the control-plane contract between Platform and Payload.

This is the single most important artifact in the Mission Platform (ADR-Z-001).
It is SemVer-versioned. A payload implements PayloadDriver; the platform
supervisor calls it. The payload NEVER grants itself privileges — it declares
needs via the capability manifest, and the platform enforces fail-closed.

Contract version: 1.0.0

Why a Protocol (typing.Protocol)?  Because it lets a payload implement the
contract without inheriting from a platform class — the payload depends on
the contract shape, not platform internals. This is the Extensibility
guarantee made mechanical (ADR-Z-001, Business Arch §4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, ClassVar, Any
from enum import Enum

CONTRACT_VERSION = "1.0.0"


class PressureLevel(str, Enum):
    """Resource-pressure signal the platform sends to a payload (amendment 4)."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class HealthState(str, Enum):
    """Payload self-reported health (amendment 4 failure contract)."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class SignedPolicy:
    """A signed configuration blob the platform hands to the payload.

    The payload treats this as authoritative — it does not self-configure.
    `signature` is opaque to the payload; the platform verified it before
    construction. Provenance is preserved for audit (Accountability).
    """
    policy: dict[str, Any]
    signature: bytes
    policy_version: str


@dataclass(frozen=True)
class ConfigureResult:
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class TickResult:
    """Outcome of one periodic tick (capture/poll)."""
    ok: bool
    artifacts: list[Any] = field(default_factory=list)  # e.g. captured image refs
    message: str = ""


@dataclass(frozen=True)
class Telemetry:
    """Standardised metrics the platform's SIEM/CMDB consumes.

    Payloads emit, the platform observes (ADR-001 AI-split applied to
    observability). Payloads do not run their own monitoring stack.
    """
    metrics: dict[str, float]
    timestamp: datetime


@dataclass(frozen=True)
class AllowedCommand:
    """A command the platform has already allowlisted for this payload.

    The payload never receives a raw command string; the platform's
    command allowlist produces an AllowedCommand. Fail-closed on unknown
    command (amendment 3).
    """
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class DegradedMode:
    """The payload's response to resource pressure (amendment 4)."""
    mode: str  # e.g. "reduce_capture_rate", "pause_video_render"
    resumed_normal: bool = False


class PayloadDriver(Protocol):
    """Every payload implements this. Called only by the platform supervisor.

    The payload is a tenant of the platform runtime, not a subroutine of it.
    """

    # The payload MUST declare the contract version it was written against.
    # The supervisor checks compatibility against its own CONTRACT_VERSION
    # via the compatibility matrix (Migration §6). Fail-closed on mismatch.
    contract_version: ClassVar[str]

    def configure(self, policy: SignedPolicy) -> ConfigureResult:
        """Apply signed policy. Called on policy change."""
        ...

    def tick(self, now: datetime) -> TickResult:
        """Do one unit of periodic domain work (capture / poll)."""
        ...

    def collect_telemetry(self) -> Telemetry:
        """Emit standardised metrics for the platform SIEM."""
        ...

    def handle_command(self, cmd: AllowedCommand) -> CommandResult:
        """Handle an already-allowlisted command. Never a raw string."""
        ...

    # --- Failure contract (ADR-001 amendment 4) ---

    def health(self) -> HealthState:
        """Self-report health. The supervisor uses this for restart/rollback."""
        ...

    def on_resource_pressure(self, level: PressureLevel) -> DegradedMode:
        """Respond to resource pressure (backpressure/degraded mode)."""
        ...
