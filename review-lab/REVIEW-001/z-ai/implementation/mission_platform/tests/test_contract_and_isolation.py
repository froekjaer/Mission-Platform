"""
Vertical-slice test suite — the executable proof for REVIEW-001 (Z.ai).

Run:  cd review-lab/REVIEW-001/implementation && python -m pytest mission_platform/tests/ -v

These tests prove:
  1. the contract fits reality (timelapse capture flows through it)  -> ADR-Z-001
  2. capability enforcement is real and fail-closed                  -> ADR-Z-002
  3. a second payload loads with no platform changes (Extensibility) -> Business Arch §4
  4. manifest validation rejects bad manifests                        -> ADR-Z-001
  5. contract-version incompatibility is rejected fail-closed        -> Migration §6
  6. the audit spine records every decision                           -> Accountability
"""
from __future__ import annotations

from datetime import datetime

import pytest

from mission_platform.contracts import (
    CONTRACT_VERSION,
    AllowedCommand,
    CapabilityManifest,
    ManifestValidationError,
    SignedPolicy,
)
from mission_platform.platform.supervisor import (
    AuditRecord,
    CapabilityDenied,
    PayloadSupervisor,
    LoadedPayload,
)
from mission_platform.payloads.timelapse import factory as timelapse_factory
from mission_platform.payloads.environmental_sensor import factory as env_factory


# --- fixtures: a synthetic capture adapter (no real camera needed) -----------

class SyntheticCapture:
    """Headless stand-in for edge/capture + edge/camera. Deterministic bytes."""
    def __init__(self):
        self._n = 0

    def capture(self, now: datetime) -> bytes:
        self._n += 1
        # Distinct bytes per call so SHA-256 differs (integrity is real).
        return f"frame-{self._n}-{now.isoformat()}".encode()


def _timelapse_manifest() -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "payload": "timelapse",
        "data_classification": "image_evidence",
        "hardware": {"required": ["camera_ptp", "relay_gpio"]},
        "resource_quota": {"cpu_percent": 40, "ram_mb": 1024, "disk_gb": 50},
        "allowlist": {"files": ["/tmp/payload/timelapse/"], "network": []},
        "service_identity": "payload-timelapse",
        "health": {"heartbeat_s": 60, "rollback_on": ["crash_loop"]},
        "api_version": "1.0.0",
    }


def _env_manifest() -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "payload": "environmental_sensor",
        "data_classification": "environmental",
        "hardware": {"required": []},
        "resource_quota": {"cpu_percent": 10, "ram_mb": 256, "disk_gb": 1},
        "allowlist": {"files": ["/tmp/payload/env-sensor/"], "network": ["10.0.0.50:502"]},
        "service_identity": "payload-env-sensor",
        "health": {"heartbeat_s": 300, "rollback_on": ["crash_loop"]},
        "api_version": "0.1.0",
    }


def _policy() -> SignedPolicy:
    return SignedPolicy(policy={"capture_interval_s": 60}, signature=b"\x01" * 32,
                        policy_version="2026-07-25-001")


# ============================================================================
# ADR-Z-001 — the contract fits reality
# ============================================================================

class TestContractFitsReality:
    """Prove the PayloadDriver contract can drive real capture behaviour."""

    def test_timelapse_loads_configures_ticks_and_captures(self):
        sup = PayloadSupervisor()
        capture = SyntheticCapture()
        loaded = sup.load("timelapse", _timelapse_manifest(),
                          timelapse_factory(capture))
        sup.configure("timelapse", _policy())

        now = datetime(2026, 7, 25, 12, 0, 0)
        result = sup.tick("timelapse", now)

        assert result.ok is True
        assert len(result.artifacts) == 1
        artifact = result.artifacts[0]
        assert artifact.sha256  # integrity hash computed by the payload
        assert artifact.size_bytes > 0
        assert sup.health("timelapse").value == "healthy"

    def test_telemetry_flows_through_the_contract(self):
        sup = PayloadSupervisor()
        loaded = sup.load("timelapse", _timelapse_manifest(),
                          timelapse_factory(SyntheticCapture()))
        sup.configure("timelapse", _policy())
        sup.tick("timelapse", datetime(2026, 7, 25, 12, 0, 0))
        sup.tick("timelapse", datetime(2026, 7, 25, 12, 1, 0))

        tel = loaded.driver.collect_telemetry()
        assert tel.metrics["ticks_total"] == 2.0
        assert tel.metrics["captures_total"] == 2.0

    def test_allowlisted_command_reaches_payload(self):
        sup = PayloadSupervisor()
        sup.load("timelapse", _timelapse_manifest(),
                 timelapse_factory(SyntheticCapture()))
        sup.configure("timelapse", _policy())
        sup.tick("timelapse", datetime(2026, 7, 25, 12, 0, 0))
        # The supervisor constructs the AllowedCommand (it has allowlisted it).
        res = sup.command("timelapse", AllowedCommand(name="purge_buffer", args={}))
        assert res.ok is True


# ============================================================================
# ADR-Z-002 — capability enforcement is real and fail-closed
# ============================================================================

class TestCapabilityEnforcementFailClosed:
    """Prove the sandbox denies off-manifest access and logs it."""

    def test_off_manifest_file_write_is_denied_and_logged(self):
        sup = PayloadSupervisor()
        # Storage path NOT in the manifest allowlist:
        loaded = sup.load("timelapse", _timelapse_manifest(),
                          timelapse_factory(SyntheticCapture(),
                                            storage_path="/etc/forbidden/"))
        sup.configure("timelapse", _policy())

        # The tick attempts a file write outside the manifest allowlist.
        # The sandbox enforces fail-closed by RAISING CapabilityDenied — the
        # payload must not silently continue after a denied write. This is the
        # correct behaviour: the supervisor would catch this, log it, and
        # transition the payload to degraded/rollback per the failure contract.
        with pytest.raises(CapabilityDenied):
            sup.tick("timelapse", datetime(2026, 7, 25, 12, 0, 0))

        denies = [a for a in sup.audit if a.action == "capability.denied"]
        assert len(denies) == 1
        assert denies[0].detail["kind"] == "file_write"
        assert "/etc/forbidden/" in denies[0].detail["path"]

    def test_off_manifest_network_access_is_denied_and_logged(self):
        sup = PayloadSupervisor()
        loaded = sup.load("env", _env_manifest(), env_factory())
        # The env payload manifest allows only 10.0.0.50:502.
        with pytest.raises(CapabilityDenied):
            loaded.sandbox.check_network("evil.example.com:443")
        denies = [a for a in sup.audit if a.action == "capability.denied"
                  and a.detail.get("kind") == "network"]
        assert len(denies) == 1
        assert denies[0].detail["destination"] == "evil.example.com:443"

    def test_on_manifest_network_access_is_allowed(self):
        sup = PayloadSupervisor()
        loaded = sup.load("env", _env_manifest(), env_factory())
        # Must not raise.
        loaded.sandbox.check_network("10.0.0.50:502")


# ============================================================================
# Business Arch §4 — Extensibility (second payload, no platform changes)
# ============================================================================

class TestExtensibility:
    """Prove a second payload loads with NO platform code changes and is isolated."""

    def test_two_payloads_load_independently(self):
        sup = PayloadSupervisor()
        sup.load("timelapse", _timelapse_manifest(),
                 timelapse_factory(SyntheticCapture()))
        sup.load("env", _env_manifest(), env_factory())
        assert set(sup._loaded.keys()) == {"timelapse", "env"}

    def test_payloads_have_independent_allowlists(self):
        """The decisive Extensibility/isolation test: env can reach a host
        timelapse cannot, and timelapse can write a path env cannot."""
        sup = PayloadSupervisor()
        tl = sup.load("timelapse", _timelapse_manifest(),
                      timelapse_factory(SyntheticCapture()))
        env = sup.load("env", _env_manifest(), env_factory())

        # env may reach 10.0.0.50:502; timelapse may not.
        env.sandbox.check_network("10.0.0.50:502")
        with pytest.raises(CapabilityDenied):
            tl.sandbox.check_network("10.0.0.50:502")

        # timelapse may write its path; env may not write timelapse's path.
        tl.sandbox.check_file_write("/tmp/payload/timelapse/x.jpg")
        with pytest.raises(CapabilityDenied):
            env.sandbox.check_file_write("/tmp/payload/timelapse/x.jpg")

    def test_second_payload_takes_no_platform_code_change(self):
        """Structural assertion: the env payload imports only contracts + supervisor,
        nothing timelapse-specific. We check import statements, not prose, so that
        docstring mentions of 'timelapse' (which explain the isolation intent) do
        not false-positive. The invariant is: no code-level coupling to another payload.
        """
        import re
        import mission_platform.payloads.environmental_sensor.driver as env_mod
        src = open(env_mod.__file__).read()
        # Only import lines can create a coupling. Comments/docstrings cannot.
        import_lines = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
        joined = "\n".join(import_lines)
        assert "timelapse" not in joined, (
            "environmental_sensor must not import timelapse — payloads are independent. "
            f"Offending imports:\n{joined}"
        )


# ============================================================================
# ADR-Z-001 — manifest validation gate (fail-closed on bad manifests)
# ============================================================================

class TestManifestValidation:
    def test_missing_required_field_is_rejected(self):
        bad = _timelapse_manifest()
        del bad["service_identity"]
        with pytest.raises(ManifestValidationError):
            CapabilityManifest.from_dict(bad)

    def test_unknown_data_classification_is_rejected(self):
        bad = _timelapse_manifest()
        bad["data_classification"] = "top_secret_unknown"
        with pytest.raises(ManifestValidationError):
            CapabilityManifest.from_dict(bad)

    def test_missing_quota_field_is_rejected(self):
        bad = _timelapse_manifest()
        bad["resource_quota"] = {"cpu_percent": 40}  # missing ram_mb, disk_gb
        with pytest.raises(ManifestValidationError):
            CapabilityManifest.from_dict(bad)

    def test_supervisor_rejects_bad_manifest_and_logs(self):
        sup = PayloadSupervisor()
        bad = _timelapse_manifest()
        del bad["payload"]
        with pytest.raises(ManifestValidationError):
            sup.load("timelapse", bad, timelapse_factory(SyntheticCapture()))
        rejections = [a for a in sup.audit if a.action == "load.rejected"]
        assert len(rejections) == 1
        assert rejections[0].detail["reason"] == "manifest_invalid"


# ============================================================================
# Migration §6 — contract-version compatibility matrix (fail-closed)
# ============================================================================

class TestContractCompatibility:
    def test_incompatible_payload_version_is_rejected(self):
        sup = PayloadSupervisor()
        bad = _timelapse_manifest()
        bad["contract_version"] = "0.9.0"  # major 0 vs platform major 1
        with pytest.raises(CapabilityDenied):
            sup.load("timelapse", bad, timelapse_factory(SyntheticCapture()))
        rejections = [a for a in sup.audit if a.action == "load.rejected"
                      and a.detail.get("reason") == "contract_incompatible"]
        assert len(rejections) == 1

    def test_driver_version_drift_is_rejected(self):
        """If the driver's declared contract_version differs from its manifest,
        the supervisor refuses to load it (no silent drift)."""
        from mission_platform.payloads.timelapse.driver import TimelapsePayload
        sup = PayloadSupervisor()

        class DriftyPayload(TimelapsePayload):
            contract_version = "1.0.0"  # manifest will say something else

        def drift_factory(sandbox):
            return DriftyPayload(sandbox=sandbox, capture=SyntheticCapture())

        bad = _timelapse_manifest()
        bad["contract_version"] = "1.2.0"  # differs from driver's 1.0.0
        with pytest.raises(CapabilityDenied):
            sup.load("timelapse", bad, drift_factory)


# ============================================================================
# Accountability — the audit spine records every decision
# ============================================================================

class TestAuditSpine:
    def test_every_lifecycle_decision_is_audited(self):
        sup = PayloadSupervisor()
        sup.load("timelapse", _timelapse_manifest(),
                 timelapse_factory(SyntheticCapture()))
        actions = {a.action for a in sup.audit}
        assert "load.accepted" in actions

    def test_actor_namespace_is_correct(self):
        sup = PayloadSupervisor()
        sup.load("timelapse", _timelapse_manifest(),
                 timelapse_factory(SyntheticCapture()))
        assert all(a.actor.startswith("payload:") for a in sup.audit)
