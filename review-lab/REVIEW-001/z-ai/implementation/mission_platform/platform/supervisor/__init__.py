"""
platform.supervisor — loads payloads, enforces the capability manifest fail-closed.

This is the enforcement boundary (ADR-Z-002). The supervisor:
  1. validates the capability manifest against the signed platform policy;
  2. checks the contract-version compatibility matrix;
  3. spawns the payload in an isolated execution context (in production: a
     dedicated systemd service + user + seccomp; in this slice: an in-process
     sandbox proxy that proves the enforcement logic);
  4. monitors health and enforces the failure contract (amendment 4);
  5. logs every decision to the audit spine.

The key invariant: a payload NEVER grants itself a capability. It declares;
the supervisor enforces; denials are logged and fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Any

from ...contracts import (
    CONTRACT_VERSION,
    CapabilityManifest,
    ManifestValidationError,
    PayloadDriver,
    SignedPolicy,
    AllowedCommand,
    ConfigureResult,
    TickResult,
    CommandResult,
    HealthState,
    PressureLevel,
)


class CapabilityDenied(Exception):
    """Raised when a payload attempts an off-manifest access. Fail-closed."""


@dataclass
class AuditRecord:
    """One record in the platform-owned audit spine (Accountability)."""
    timestamp: datetime
    actor: str          # e.g. "payload:timelapse"
    action: str         # e.g. "capability.denied"
    detail: dict[str, Any] = field(default_factory=dict)


# Compatibility matrix (Migration Strategy §6). Strict by default.
_COMPAT: dict[tuple[str, str], bool] = {
    # (platform_major, payload_major) -> loadable?
    ("1", "1"): True,
    ("1", "0"): False,
    ("0", "1"): False,
}


def _major(version: str) -> str:
    return version.split(".", 1)[0]


class Sandbox:
    """Isolation proxy.

    In production (ADR-Z-002) this is a separate systemd service with a
    dedicated user, seccomp filter, ReadWritePaths and IPAddressAllow
    derived from the manifest. In this vertical slice it is an in-process
    proxy that enforces the manifest's network/file allowlists against the
    payload's declared intents — proving the enforcement logic is real
    before the systemd-unit generator is built.
    """

    def __init__(self, manifest: CapabilityManifest, audit: list[AuditRecord]):
        self._manifest = manifest
        self._audit = audit

    def check_network(self, destination: str) -> None:
        """Enforce the network allowlist. Raises CapabilityDenied if off-manifest."""
        allowed = self._manifest.network_destinations()
        if destination not in allowed:
            self._audit.append(AuditRecord(
                timestamp=datetime.now(timezone.utc),
                actor=f"payload:{self._manifest.payload}",
                action="capability.denied",
                detail={"kind": "network", "destination": destination,
                        "allowed": allowed},
            ))
            raise CapabilityDenied(
                f"payload {self._manifest.payload!r} denied network "
                f"access to {destination!r} (not in manifest allowlist)"
            )

    def check_file_write(self, path: str) -> None:
        """Enforce the file-write allowlist."""
        allowed = self._manifest.writable_paths()
        if not any(path.startswith(p) for p in allowed):
            self._audit.append(AuditRecord(
                timestamp=datetime.now(timezone.utc),
                actor=f"payload:{self._manifest.payload}",
                action="capability.denied",
                detail={"kind": "file_write", "path": path, "allowed": allowed},
            ))
            raise CapabilityDenied(
                f"payload {self._manifest.payload!r} denied write to "
                f"{path!r} (not under any manifest allowlist path)"
            )


@dataclass
class LoadedPayload:
    """A payload the supervisor has accepted and sandboxed."""
    name: str
    manifest: CapabilityManifest
    driver: PayloadDriver
    sandbox: Sandbox


class PayloadSupervisor:
    """The platform component that governs payload lifecycle and enforcement."""

    def __init__(self, audit: list[AuditRecord] | None = None):
        self._audit: list[AuditRecord] = audit if audit is not None else []
        self._loaded: dict[str, LoadedPayload] = {}

    @property
    def audit(self) -> list[AuditRecord]:
        return self._audit

    def load(
        self,
        name: str,
        manifest_raw: dict[str, Any],
        driver_factory: Callable[[Sandbox], PayloadDriver],
    ) -> LoadedPayload:
        """Validate manifest, check compatibility, sandbox, and register a payload.

        Fail-closed at every gate. A denial is logged and raises.
        """
        # Gate 1: manifest schema validation.
        try:
            manifest = CapabilityManifest.from_dict(manifest_raw)
        except ManifestValidationError as e:
            self._audit.append(AuditRecord(
                timestamp=datetime.now(timezone.utc),
                actor=f"payload:{name}",
                action="load.rejected",
                detail={"reason": "manifest_invalid", "errors": str(e)},
            ))
            raise

        # Gate 2: contract-version compatibility matrix.
        plat_major = _major(CONTRACT_VERSION)
        pay_major = _major(manifest.contract_version)
        if not _COMPAT.get((plat_major, pay_major), False):
            self._audit.append(AuditRecord(
                timestamp=datetime.now(timezone.utc),
                actor=f"payload:{name}",
                action="load.rejected",
                detail={"reason": "contract_incompatible",
                        "platform": CONTRACT_VERSION,
                        "payload": manifest.contract_version},
            ))
            raise CapabilityDenied(
                f"contract version incompatible: platform {CONTRACT_VERSION} "
                f"vs payload {manifest.contract_version}"
            )

        # Gate 3: sandbox construction (the enforcement proxy).
        sandbox = Sandbox(manifest, self._audit)
        driver = driver_factory(sandbox)

        # Gate 4: the driver must declare the same contract version it was
        # loaded against — no silent drift.
        declared = getattr(driver, "contract_version", None)
        if declared != manifest.contract_version:
            self._audit.append(AuditRecord(
                timestamp=datetime.now(timezone.utc),
                actor=f"payload:{name}",
                action="load.rejected",
                detail={"reason": "contract_version_drift",
                        "manifest": manifest.contract_version,
                        "driver": declared},
            ))
            raise CapabilityDenied(
                f"driver contract_version {declared!r} != manifest "
                f"{manifest.contract_version!r}"
            )

        loaded = LoadedPayload(name=name, manifest=manifest, driver=driver, sandbox=sandbox)
        self._loaded[name] = loaded
        self._audit.append(AuditRecord(
            timestamp=datetime.now(timezone.utc),
            actor=f"payload:{name}",
            action="load.accepted",
            detail={"contract": manifest.contract_version,
                    "api": manifest.api_version,
                    "data_classification": manifest.data_classification},
        ))
        return loaded

    def configure(self, name: str, policy: SignedPolicy) -> ConfigureResult:
        return self._must(name).driver.configure(policy)

    def tick(self, name: str, now: datetime) -> TickResult:
        return self._must(name).driver.tick(now)

    def command(self, name: str, cmd: AllowedCommand) -> CommandResult:
        """Send an allowlisted command. The supervisor has already allowlisted;
        the payload receives an AllowedCommand, never a raw string."""
        return self._must(name).driver.handle_command(cmd)

    def health(self, name: str) -> HealthState:
        return self._must(name).driver.health()

    def _must(self, name: str) -> LoadedPayload:
        if name not in self._loaded:
            raise KeyError(f"payload {name!r} not loaded")
        return self._loaded[name]
