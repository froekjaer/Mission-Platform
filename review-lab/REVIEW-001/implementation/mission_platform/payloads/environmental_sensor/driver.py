"""
payloads.environmental_sensor.driver — a STUB second payload.

Its entire purpose is to prove Extensibility (Business Arch §4): a second
payload can be added by implementing the contract ONLY, with NO platform
code changes, and it loads, is isolated, and cannot read timelapse's data.

It does not represent a real environmental sensor. It is deliberately
minimal — a proof, not a product. (Also exercises ADR-0007's review
trigger, pulled forward as proof per Migration Step 5.)

Note: this payload declares a NETWORK destination in its manifest, unlike
timelapse. That lets the enforcement test (test_payload_isolation) prove
that environmental_sensor's allowlist is independent of timelapse's.
"""
from __future__ import annotations

from datetime import datetime, timezone

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


class EnvironmentalSensorPayload:
    contract_version = CONTRACT_VERSION

    def __init__(self, sandbox: Sandbox):
        self._sandbox = sandbox
        self._policy: SignedPolicy | None = None
        self._readings: list[float] = []
        self._health = HealthState.HEALTHY
        self._ticks = 0

    def configure(self, policy: SignedPolicy) -> ConfigureResult:
        self._policy = policy
        return ConfigureResult(ok=True)

    def tick(self, now: datetime) -> TickResult:
        assert self._policy is not None
        self._ticks += 1
        # A real sensor would read hardware; here we synthesise a reading.
        reading = 20.0 + 0.1 * (self._ticks % 10)
        self._readings.append(reading)
        return TickResult(ok=True, message=f"reading={reading:.1f}")

    def collect_telemetry(self) -> Telemetry:
        return Telemetry(
            metrics={"ticks_total": float(self._ticks),
                     "last_reading": float(self._readings[-1]) if self._readings else 0.0},
            timestamp=datetime.now(timezone.utc),
        )

    def handle_command(self, cmd: AllowedCommand) -> CommandResult:
        return CommandResult(ok=False, message="no commands supported")

    def health(self) -> HealthState:
        return self._health

    def on_resource_pressure(self, level: PressureLevel) -> DegradedMode:
        return DegradedMode(mode="normal", resumed_normal=True)


def factory():
    def _build(sandbox: Sandbox) -> EnvironmentalSensorPayload:
        return EnvironmentalSensorPayload(sandbox=sandbox)
    return _build
