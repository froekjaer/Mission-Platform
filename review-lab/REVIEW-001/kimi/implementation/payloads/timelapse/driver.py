#!/usr/bin/env python3
"""Timelapse payload driver (PoC) — first functional payload of Mission Platform.

Speaks the control plane (JSON lines on stdin/stdout) and the data plane
(spool dir + SHA-256 sidecars). In the PoC the "camera" is synthetic: the
artifact is a deterministic pseudo-image so tests are reproducible without
hardware. The structure mirrors the production evidence model in TimeLapse
Pro (pre-XMP SHA-256 sidecar per capture).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

SCHEMA_CONTROL = "mission.control.v1"
SCHEMA_ENVELOPE = "mission.data-envelope.v1"


def _synthetic_frame(seq: int) -> bytes:
    """Deterministic stand-in for a Nikon Z30 JPEG."""
    return hashlib.sha256(f"timelapse-frame-{seq}".encode()).digest() * 64


def run(spool_dir: str) -> None:
    spool = Path(spool_dir)
    spool.mkdir(parents=True, exist_ok=True)
    seq = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("schema") != SCHEMA_CONTROL:
            continue
        cmd = msg.get("cmd")
        if cmd == "capture.now":
            seq += 1
            frame = _synthetic_frame(seq)
            name = f"capture_{seq:06d}.img"
            (spool / name).write_bytes(frame)
            sidecar = {
                "schema": SCHEMA_ENVELOPE,
                "artifact": name,
                "sha256": hashlib.sha256(frame).hexdigest(),
                "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "classification": "image",
            }
            (spool / f"{name}.sha256.json").write_text(json.dumps(sidecar))
            print(json.dumps({"schema": SCHEMA_CONTROL, "status": "ok",
                              "artifact": name, "sha256": sidecar["sha256"]}), flush=True)
        elif cmd == "status.get":
            print(json.dumps({"schema": SCHEMA_CONTROL, "status": "ok",
                              "telemetry": {"captures": seq,
                                            "quality": {"flag": "ok", "blur_score": 150.5}}}), flush=True)
        else:
            print(json.dumps({"schema": SCHEMA_CONTROL, "status": "rejected", "cmd": cmd}), flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
