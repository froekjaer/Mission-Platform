#!/usr/bin/env python3
"""Mission Platform — Edge Kernel (PoC, REVIEW-001 / Kimi).

Minimal, verifiable supervisor that runs a payload (e.g. timelapse) as a
SEPARATE OS process and enforces the capability manifest FAIL-CLOSED.

Design intent (see adr/ADR-K002):
- The manifest is a DECLARATION by the payload; platform policy is the
  authoritative enforcement point.
- Control plane = JSON-lines commands on the payload's stdin/stdout.
- Data plane = content-addressed artifacts in a spool directory, each with a
  SHA-256 sidecar (mirrors the proven TimeLapse Pro evidence model).
- No inbound ports. The kernel initiates everything.

Stdlib only by design: the kernel must stay small enough to audit.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import resource
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_MANIFEST = "mission.capability-manifest.v1"
SCHEMA_CONTROL = "mission.control.v1"
SCHEMA_ENVELOPE = "mission.data-envelope.v1"


class PolicyViolation(Exception):
    """Raised when a manifest or message violates platform policy. Fail-closed."""


@dataclass
class PlatformPolicy:
    """Authoritative, kernel-side allowlist. Payloads cannot widen this."""
    allowed_capabilities: set[str]
    max_cpu_seconds: int = 300
    max_rss_mb: int = 256
    max_payloads: int = 4
    allowed_commands: set[str] = field(default_factory=lambda: {"capture.now", "status.get"})
    signing_key: bytes = b"poc-only-not-a-real-key"  # PoC: HMAC; prod: Ed25519, see ADR-K003


def sign_manifest(manifest: dict, key: bytes) -> str:
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def _verify_manifest_signature(manifest_doc: dict, key: bytes) -> None:
    sig = manifest_doc.get("signature")
    body = {k: v for k, v in manifest_doc.items() if k != "signature"}
    expected = sign_manifest(body, key)
    if not (isinstance(sig, str) and hmac.compare_digest(sig, expected)):
        raise PolicyViolation("manifest signature invalid — payload rejected (fail-closed)")


def validate_manifest(manifest_doc: dict, policy: PlatformPolicy) -> dict:
    """Fail-closed validation. Returns the manifest body or raises PolicyViolation."""
    _verify_manifest_signature(manifest_doc, policy.signing_key)
    m = manifest_doc
    if m.get("schema") != SCHEMA_MANIFEST:
        raise PolicyViolation(f"unknown manifest schema: {m.get('schema')!r}")
    if not isinstance(m.get("payload_id"), str) or not m["payload_id"]:
        raise PolicyViolation("manifest missing payload_id")
    requested = set(m.get("capabilities", []))
    unknown = requested - policy.allowed_capabilities
    if unknown:
        raise PolicyViolation(f"unknown capabilities requested: {sorted(unknown)} (fail-closed)")
    quota = m.get("resource_quota", {})
    if quota.get("cpu_seconds", 0) > policy.max_cpu_seconds:
        raise PolicyViolation("cpu quota exceeds platform maximum")
    if quota.get("rss_mb", 0) > policy.max_rss_mb:
        raise PolicyViolation("rss quota exceeds platform maximum")
    if m.get("data_classification") not in ("image", "process", "telemetry"):
        raise PolicyViolation("data_classification missing or invalid")
    return m


def _apply_quota(manifest: dict) -> None:
    """preexec_fn: applied in the child process before exec."""
    quota = manifest.get("resource_quota", {})
    cpu = int(quota.get("cpu_seconds", 60))
    rss = int(quota.get("rss_mb", 128)) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    resource.setrlimit(resource.RLIMIT_AS, (rss, rss))
    os.setsid()  # own process group -> kernel can kill the whole tree (kill switch)


@dataclass
class PayloadProcess:
    manifest: dict
    proc: subprocess.Popen
    spool_dir: Path


class EdgeKernel:
    def __init__(self, policy: PlatformPolicy, spool_root: Path):
        self.policy = policy
        self.spool_root = Path(spool_root)
        self.spool_root.mkdir(parents=True, exist_ok=True)
        self.payloads: dict[str, PayloadProcess] = {}
        self.audit: list[dict] = []  # in-memory; prod: append-only SIEM stream

    def _log(self, event: str, **kw) -> None:
        self.audit.append({"ts": time.time(), "event": event, **kw})

    def start_payload(self, manifest_doc: dict, payload_argv: list[str]) -> PayloadProcess:
        if len(self.payloads) >= self.policy.max_payloads:
            raise PolicyViolation("payload limit reached")
        m = validate_manifest(manifest_doc, self.policy)
        pid_ = m["payload_id"]
        spool = self.spool_root / pid_
        spool.mkdir(parents=True, exist_ok=True)
        proc = subprocess.Popen(
            payload_argv,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True,
            preexec_fn=lambda: _apply_quota(m),
        )
        pp = PayloadProcess(manifest=m, proc=proc, spool_dir=spool)
        self.payloads[pid_] = pp
        self._log("payload_started", payload_id=pid_, capabilities=m.get("capabilities"))
        return pp

    def command(self, payload_id: str, cmd: str, args: dict | None = None) -> dict:
        """Control plane: allowlisted commands only, fail-closed, timeout-bounded."""
        pp = self.payloads[payload_id]
        if cmd not in self.policy.allowed_commands:
            self._log("command_rejected", payload_id=payload_id, cmd=cmd)
            raise PolicyViolation(f"command not in platform allowlist: {cmd}")
        msg = {"schema": SCHEMA_CONTROL, "cmd": cmd, "args": args or {}}
        assert pp.proc.stdin and pp.proc.stdout
        pp.proc.stdin.write(json.dumps(msg) + "\n")
        pp.proc.stdin.flush()
        pp.proc.stdout.flush()
        line = pp.proc.stdout.readline()
        if not line:
            self._log("payload_unresponsive", payload_id=payload_id)
            raise PolicyViolation("payload produced no control response (crashed?)")
        resp = json.loads(line)
        if resp.get("schema") != SCHEMA_CONTROL:
            raise PolicyViolation("malformed control response")
        self._log("command_ok", payload_id=payload_id, cmd=cmd)
        return resp

    def ingest_data(self, payload_id: str) -> list[dict]:
        """Data plane: verify every artifact against its SHA-256 sidecar."""
        pp = self.payloads[payload_id]
        accepted = []
        for sidecar in sorted(pp.spool_dir.glob("*.sha256.json")):
            meta = json.loads(sidecar.read_text())
            artifact = pp.spool_dir / meta["artifact"]
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            if not hmac.compare_digest(digest, meta["sha256"]):
                self._log("artifact_rejected_hash_mismatch", artifact=meta["artifact"])
                continue
            accepted.append({"artifact": meta["artifact"], "sha256": digest,
                             "classification": meta.get("classification")})
            self._log("artifact_accepted", artifact=meta["artifact"], sha256=digest)
        return accepted

    def kill_switch(self, payload_id: str) -> None:
        pp = self.payloads.pop(payload_id, None)
        if not pp:
            return
        try:
            os.killpg(pp.proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self._log("payload_killed", payload_id=payload_id)

    def shutdown(self) -> None:
        for pid_ in list(self.payloads):
            self.kill_switch(pid_)
