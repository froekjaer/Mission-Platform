"""Fail-closed admission tests — the security core of the contract set.

Every test asserts REFUSAL: the platform must deny anything it does not
positively recognise and authorise (ADR-CL-004; source ADR-001 amendment 3).
"""
import copy

import pytest

from conftest import NODE_KEY, make_policy_doc
from contracts.manifest import ManifestRejected
from payloads.timelapse.driver import TimelapseDriver
from platform_host.policy import PolicyUnverified, load_verified_policy, sign_policy
from platform_host.supervisor import PayloadState


def timelapse_factory(manifest, sink):
    return TimelapseDriver(sink)


def test_unknown_capability_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["capabilities"].append("actuator.valve")  # not in v1 vocabulary, by design
    with pytest.raises(ManifestRejected, match="unknown capability"):
        supervisor.admit(doc, timelapse_factory)
    assert supervisor.audit_log[-1].outcome == "REFUSED"


def test_unknown_top_level_field_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["extra_privileges"] = ["root"]
    with pytest.raises(ManifestRejected, match="unknown field"):
        supervisor.admit(doc, timelapse_factory)


def test_capability_not_granted_by_node_policy_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["capabilities"] = ["camera.usb", "sdr.rx"]  # known, but node policy denies sdr.rx
    with pytest.raises(ManifestRejected, match="not granted by node policy"):
        supervisor.admit(doc, timelapse_factory)


def test_quota_above_ceiling_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["quotas"]["mem_mb"] = 4096  # ceiling is 1024
    with pytest.raises(ManifestRejected, match="exceeds node ceiling"):
        supervisor.admit(doc, timelapse_factory)


def test_unsupported_contract_major_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["contracts"]["control"] = "2.x"
    with pytest.raises(ManifestRejected, match="unsupported"):
        supervisor.admit(doc, timelapse_factory)


def test_personal_data_on_timeseries_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["channels"][1]["classification"] = "personal-images"
    with pytest.raises(ManifestRejected, match="personal data forbidden"):
        supervisor.admit(doc, timelapse_factory)


def test_duplicate_channel_refused(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["channels"].append(copy.deepcopy(doc["channels"][0]))
    with pytest.raises(ManifestRejected, match="duplicate channel"):
        supervisor.admit(doc, timelapse_factory)


def test_tampered_node_policy_refused():
    doc = make_policy_doc()
    sig = sign_policy(doc, NODE_KEY)
    doc["allowed_capabilities"].append("sdr.rx")  # tamper after signing
    with pytest.raises(PolicyUnverified):
        load_verified_policy(doc, sig, NODE_KEY)


def test_missing_signature_refused():
    doc = make_policy_doc()
    with pytest.raises(PolicyUnverified):
        load_verified_policy(doc, "", NODE_KEY)


def test_refused_payload_is_never_instantiated(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["capabilities"] = ["gpio.read"]  # known but not granted
    instantiated = []

    def factory(manifest, sink):
        instantiated.append(True)
        return TimelapseDriver(sink)

    with pytest.raises(ManifestRejected):
        supervisor.admit(doc, factory)
    assert instantiated == []  # fail closed: no driver object ever existed


def test_admission_success_is_audited(supervisor, timelapse_manifest):
    managed = supervisor.admit(timelapse_manifest, timelapse_factory)
    assert managed.state is PayloadState.ADMITTED
    assert supervisor.audit_log[-1].action == "admit"
    assert supervisor.audit_log[-1].outcome == "OK"
