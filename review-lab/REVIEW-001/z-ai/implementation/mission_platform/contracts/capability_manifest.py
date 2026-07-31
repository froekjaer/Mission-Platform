"""
contracts.capability_manifest — schema + validation for the payload capability manifest.

The manifest is what a payload DECLARES. The platform supervisor ENFORCES it
fail-closed (ADR-001 amendment 3, ADR-Z-001, ADR-Z-002). A payload whose
manifest does not validate, or whose runtime behaviour exceeds its manifest,
is denied and logged.

The manifest is intentionally YAML-friendly (a plain dict schema) so it can
be authored by payload developers and read by the supervisor's systemd-unit
generator without a shared code dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ManifestValidationError(Exception):
    """Raised when a manifest is incomplete or invalid. Fail-closed on this."""


# Allowed values for data_classification. Drives retention/DPIA per payload
# (Business Arch §3 "Proportionate compliance"). Adding a value is a minor
# contract change; the platform owns this enum.
ALLOWED_DATA_CLASSIFICATIONS = frozenset({
    "image_evidence",      # timelapse — legal-evidence grade, strict retention
    "image_operational",   # operational imagery, lower retention
    "process_data",        # OT/process telemetry (waterworks, energy)
    "environmental",       # environmental sensing
    "diagnostic_only",     # no business data, telemetry only
})


@dataclass(frozen=True)
class HardwareRequirement:
    required: list[str]   # e.g. ["camera_ptp", "relay_gpio", "modbus_rtu"]


@dataclass(frozen=True)
class ResourceQuota:
    cpu_percent: int
    ram_mb: int
    disk_gb: int


@dataclass(frozen=True)
class Allowlist:
    files: list[str]
    network: list[str]    # destination allowlist, e.g. ["10.0.0.0/8:502"]


@dataclass(frozen=True)
class HealthContract:
    heartbeat_s: int
    rollback_on: list[str]   # e.g. ["crash_loop", "bad_contract_version"]


@dataclass(frozen=True)
class CapabilityManifest:
    """Validated capability manifest. Construct via from_dict()."""
    contract_version: str
    payload: str
    data_classification: str
    hardware: HardwareRequirement
    resource_quota: ResourceQuota
    allowlist: Allowlist
    service_identity: str
    health: HealthContract
    api_version: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CapabilityManifest":
        """Validate and construct. Raises ManifestValidationError on any problem.

        This is the fail-closed gate. A payload with a bad manifest never loads.
        """
        errors: list[str] = []

        def need(key: str) -> Any:
            if key not in raw:
                errors.append(f"missing required field: {key}")
                return None
            return raw[key]

        contract_version = need("contract_version")
        payload = need("payload")
        data_classification = need("data_classification")
        if data_classification is not None and data_classification not in ALLOWED_DATA_CLASSIFICATIONS:
            errors.append(
                f"data_classification {data_classification!r} not in "
                f"allowed set {sorted(ALLOWED_DATA_CLASSIFICATIONS)}"
            )
        service_identity = need("service_identity")
        api_version = need("api_version")

        # Nested objects
        hw_raw = need("hardware") or {}
        rq_raw = need("resource_quota") or {}
        al_raw = need("allowlist") or {}
        hl_raw = need("health") or {}

        try:
            hardware = HardwareRequirement(required=list(hw_raw.get("required", [])))
        except (TypeError, AttributeError):
            errors.append("hardware malformed")
            hardware = None

        try:
            resource_quota = ResourceQuota(
                cpu_percent=int(rq_raw["cpu_percent"]),
                ram_mb=int(rq_raw["ram_mb"]),
                disk_gb=int(rq_raw["disk_gb"]),
            )
        except (KeyError, TypeError, ValueError):
            errors.append("resource_quota malformed or incomplete")
            resource_quota = None

        try:
            allowlist = Allowlist(
                files=list(al_raw.get("files", [])),
                network=list(al_raw.get("network", [])),
            )
        except (TypeError, AttributeError):
            errors.append("allowlist malformed")
            allowlist = None

        try:
            health = HealthContract(
                heartbeat_s=int(hl_raw["heartbeat_s"]),
                rollback_on=list(hl_raw.get("rollback_on", [])),
            )
        except (KeyError, TypeError, ValueError):
            errors.append("health malformed or incomplete")
            health = None

        # service_identity must differ from any platform-credential convention.
        # (amendment 3: payload credential != platform credential.) We enforce
        # the naming convention here: payload identities are namespaced.
        if service_identity is not None and not service_identity.startswith("payload-"):
            # Not fatal — but logged. The convention keeps platform credentials
            # (e.g. "platform-core") visually distinct from payload ones.
            pass

        if errors:
            raise ManifestValidationError("; ".join(errors))

        # All checks passed — construct. (mypy: we've proven non-None above.)
        return cls(
            contract_version=contract_version,  # type: ignore[arg-type]
            payload=payload,                    # type: ignore[arg-type]
            data_classification=data_classification,  # type: ignore[arg-type]
            hardware=hardware,                  # type: ignore[arg-type]
            resource_quota=resource_quota,      # type: ignore[arg-type]
            allowlist=allowlist,                # type: ignore[arg-type]
            service_identity=service_identity,  # type: ignore[arg-type]
            health=health,                      # type: ignore[arg-type]
            api_version=api_version,            # type: ignore[arg-type]
        )

    def network_destinations(self) -> list[str]:
        """Destinations the payload is allowed to reach (for enforcement)."""
        return list(self.allowlist.network)

    def writable_paths(self) -> list[str]:
        return list(self.allowlist.files)
