"""
payloads.timelapse.driver — the first payload, wrapping capture logic behind
the PayloadDriver contract.

This is the "wrap" of Migration Step 0: the existing timelapse capture/tick
behaviour (in timelapse-pro: edge/capture + edge/camera) is represented by
a CaptureAdapter and driven through the contract. No real camera is needed
for the slice — the adapter is injectable so contract tests run headless.

Key points:
  - The payload implements contracts.PayloadDriver; it does NOT inherit
    platform internals (Extensibility).
  - capture writes go through the sandbox (enforced file allowlist).
  - the payload computes the SHA-256 integrity hash; the platform stores it
    (Logical Arch §4.1 — payload declares evidence-grade, platform verifies).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Protocol

from ...contracts import (
    CONTRACT_VERSION,
    AllowedCommand,
    CommandResult,
    ConfigureResult,
    DegradedMode,
    HealthState,
    PressureLevel,
    SignedPolicy,
    Telemetry,
    TickResult,
)
from ...platform.supervisor import Sandbox


class CaptureAdapter(Protocol):
    """What the payload needs from the (existing, wrapped) capture subsystem.

    In production this wraps edge/capture + edge/camera. In the slice it is
    an injectable callable so tests run without hardware.
    """

    def capture(self, now: datetime) -> bytes:
        """Return raw image bytes for one capture at `now`."""
        ...


@dataclass
class CapturedArtifact:
    """One captured image + its integrity hash, handed to the data plane."""
    timestamp: datetime
    sha256: str
    size_bytes: int


class TimelapsePayload:
    """Implements contracts.PayloadDriver. contract_version is a ClassVar."""

    contract_version = CONTRACT_VERSION  # declared on the class

    def __init__(self, sandbox: Sandbox, capture: CaptureAdapter,
                 storage_path: str = "/tmp/payload/timelapse/"):
        self._sandbox = sandbox
        self._capture = capture
        self._storage_path = storage_path
        self._policy: SignedPolicy | None = None
        self._captures: list[CapturedArtifact] = []
        self._health = HealthState.HEALTHY
        self._ticks = 0
        self._captures_failed = 0

    # --- PayloadDriver ---

    def configure(self, policy: SignedPolicy) -> ConfigureResult:
        # The payload applies signed policy; it does not self-configure.
        self._policy = policy
        return ConfigureResult(ok=True, message="configured")

    def tick(self, now: datetime) -> TickResult:
        assert self._policy is not None, "tick before configure"
        self._ticks += 1
        try:
            raw = self._capture.capture(now)
        except Exception as e:  # noqa: BLE001 - failure contract
            self._captures_failed += 1
            self._health = HealthState.DEGRADED
            return TickResult(ok=False, message=f"capture failed: {e}")

        # Payload computes the integrity hash (evidence-grade declaration).
        digest = hashlib.sha256(raw).hexdigest()
        artifact = CapturedArtifact(
            timestamp=now, sha256=digest, size_bytes=len(raw),
        )

        # File write is enforced by the sandbox (fail-closed if off-manifest).
        dest = f"{self._storage_path}{now.isoformat()}_{digest[:8]}.jpg"
        self._sandbox.check_file_write(dest)

        self._captures.append(artifact)
        self._health = HealthState.HEALTHY
        return TickResult(ok=True, artifacts=[artifact], message="captured")

    def collect_telemetry(self) -> Telemetry:
        return Telemetry(
            metrics={
                "ticks_total": float(self._ticks),
                "captures_total": float(len(self._captures)),
                "captures_failed_total": float(self._captures_failed),
            },
            timestamp=datetime.now(timezone.utc),
        )

    def handle_command(self, cmd: AllowedCommand) -> CommandResult:
        # The supervisor has already allowlisted cmd.name. The payload
        # handles only known commands; unknown is a programming error.
        if cmd.name == "purge_buffer":
            n = len(self._captures)
            self._captures.clear()
            return CommandResult(ok=True, message=f"purged {n}")
        return CommandResult(ok=False, message=f"unknown command {cmd.name!r}")

    # --- Failure contract (amendment 4) ---

    def health(self) -> HealthState:
        return self._health

    def on_resource_pressure(self, level: PressureLevel) -> DegradedMode:
        if level == PressureLevel.CRITICAL:
            return DegradedMode(mode="pause_capture", resumed_normal=False)
        if level == PressureLevel.WARNING:
            return DegradedMode(mode="reduce_capture_rate", resumed_normal=False)
        return DegradedMode(mode="normal", resumed_normal=True)


def factory(capture: CaptureAdapter, storage_path: str = "/tmp/payload/timelapse/"):
    """Return a driver_factory closure for the supervisor.

    The supervisor calls factory(sandbox) -> PayloadDriver. We close over the
    capture adapter so the payload has its domain collaborator injected.
    """
    def _build(sandbox: Sandbox) -> TimelapsePayload:
        return TimelapsePayload(sandbox=sandbox, capture=capture,
                                storage_path=storage_path)
    return _build
