#!/usr/bin/env python3
"""Vertical-slice tests for the Mission Platform PoC (Kimi, REVIEW-001).

Run:  python3 tests/test_vertical_slice.py
Evidence: each PASS line is a runtime claim; keep output in evidence/.

Covers the load-bearing invariants:
 1. A payload runs as a SEPARATE OS process (fault containment).
 2. An unsigned/tampered manifest is REJECTED (fail-closed).
 3. Unknown capabilities are REJECTED (fail-closed).
 4. Non-allowlisted commands are REJECTED (control plane fail-closed).
 5. A capture produces a data artifact whose SHA-256 sidecar VERIFIES.
 6. A corrupted artifact is NOT accepted by the data plane.
"""
import copy
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "implementation" / "edge_kernel"))
from kernel import EdgeKernel, PlatformPolicy, PolicyViolation, sign_manifest  # noqa: E402

DRIVER = str(Path(__file__).resolve().parent.parent / "implementation" / "payloads" / "timelapse" / "driver.py")

POLICY = PlatformPolicy(allowed_capabilities={"camera.ptp", "gpio.relay"})

BASE_MANIFEST = {
    "schema": "mission.capability-manifest.v1",
    "payload_id": "timelapse",
    "version": "0.1.0",
    "capabilities": ["camera.ptp", "gpio.relay"],
    "resource_quota": {"cpu_seconds": 60, "rss_mb": 128},
    "data_classification": "image",
    "health": {"restart": "on-failure", "max_restarts": 3},
}

results = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))


def signed(m: dict) -> dict:
    m = copy.deepcopy(m)
    m["signature"] = sign_manifest(m, POLICY.signing_key)
    return m


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="mp-poc-"))
    kernel = EdgeKernel(POLICY, tmp / "spool")

    bad = signed(BASE_MANIFEST)
    bad["capabilities"] = ["camera.ptp", "gpio.relay", "net.raw_socket"]
    try:
        kernel.start_payload(bad, [sys.executable, DRIVER, "x"])
        check("tampered manifest rejected (fail-closed)", False)
    except PolicyViolation:
        check("tampered manifest rejected (fail-closed)", True)

    evil = copy.deepcopy(BASE_MANIFEST)
    evil["capabilities"] = ["net.raw_socket"]
    try:
        kernel.start_payload(signed(evil), [sys.executable, DRIVER, "x"])
        check("unknown capability rejected (fail-closed)", False)
    except PolicyViolation:
        check("unknown capability rejected (fail-closed)", True)

    pp = kernel.start_payload(signed(BASE_MANIFEST), [sys.executable, DRIVER, str(tmp / "spool" / "timelapse")])
    check("payload runs as separate OS process", pp.proc.pid > 0 and pp.proc.poll() is None,
          f"pid={pp.proc.pid}")

    try:
        kernel.command("timelapse", "shell.exec", {"c": "id"})
        check("non-allowlisted command rejected", False)
    except PolicyViolation:
        check("non-allowlisted command rejected", True)

    resp = kernel.command("timelapse", "capture.now")
    accepted = kernel.ingest_data("timelapse")
    check("capture artifact accepted with verified SHA-256",
          resp["status"] == "ok" and len(accepted) == 1
          and accepted[0]["sha256"] == resp["sha256"],
          f"sha256={resp['sha256'][:16]}…")

    status = kernel.command("timelapse", "status.get")
    check("telemetry via control plane", status["telemetry"]["captures"] == 1)

    artifact = tmp / "spool" / "timelapse" / "capture_000001.img"
    artifact.write_bytes(b"tampered")
    accepted2 = kernel.ingest_data("timelapse")
    check("corrupted artifact rejected by data plane", len(accepted2) == 0)

    kernel.kill_switch("timelapse")
    check("kill switch terminates payload", pp.proc.wait(timeout=5) is not None)

    audit_events = {e["event"] for e in kernel.audit}
    check("decisions logged to audit trail",
          {"payload_started", "command_rejected", "artifact_accepted",
           "artifact_rejected_hash_mismatch", "payload_killed"} <= audit_events)

    kernel.shutdown()
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
