"""Timelapse payload driver — the first Mission Package (vertical slice).

Imports ONLY from contracts (anti-coupling invariant). The MockCamera stands
in for the gphoto2/Nikon HAL grant; the capture loop, policy handling,
telemetry and command surface mirror the source system's edge capture flow
(traceability: edge/camera, edge/capture at baseline eed9e3c8).
"""
from __future__ import annotations

import datetime as _dt
import threading

from contracts.control import (
    Command,
    CommandRejected,
    CommandResult,
    HealthReport,
    HealthStatus,
    PayloadDriver,
    PayloadPolicy,
    PolicyRejected,
)
from contracts.data import Backpressure, BlobMeta, DataSink, TimeseriesPoint

_JPEG_SOI = b"\xff\xd8\xff\xe0"  # mock JPEG header


class MockCamera:
    """Stands in for the camera.usb capability grant."""

    def capture(self) -> bytes:
        body = _dt.datetime.now(_dt.timezone.utc).isoformat().encode()
        return _JPEG_SOI + body


class TimelapseDriver(PayloadDriver):
    ALLOWED_COMMANDS = {"capture_now", "get_stats"}

    def __init__(self, sink: DataSink, camera: MockCamera | None = None) -> None:
        self._sink = sink
        self._camera = camera or MockCamera()
        self._interval_s: float = 60.0
        self._configured = False
        self._running = threading.Event()
        self._stop_signal = threading.Event()
        self._thread: threading.Thread | None = None
        self._captures_ok = 0
        self._captures_failed = 0
        self._lock = threading.Lock()

    # -- control contract ----------------------------------------------------
    def configure(self, policy: PayloadPolicy) -> None:
        interval = policy.settings.get("interval_s")
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise PolicyRejected(f"interval_s must be positive number, got {interval!r}")
        self._interval_s = float(interval)
        self._configured = True

    def start(self) -> None:
        if not self._configured:
            raise PolicyRejected("start() before configure() (fail closed)")
        if self._running.is_set():
            return
        self._stop_signal.clear()
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self, deadline_s: float) -> None:
        self._running.clear()
        self._stop_signal.set()
        if self._thread is not None:
            self._thread.join(timeout=deadline_s)
            self._thread = None

    def health(self) -> HealthReport:
        with self._lock:
            ok, failed = self._captures_ok, self._captures_failed
        total = ok + failed
        if total and failed / total > 0.5:
            status = HealthStatus.FAILED
        elif failed:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.OK
        return HealthReport(status=status, detail=f"{ok} ok / {failed} failed",
                            metrics={"captures_ok": ok, "captures_failed": failed})

    def handle_command(self, cmd: Command) -> CommandResult:
        if cmd.name not in self.ALLOWED_COMMANDS:
            raise CommandRejected(f"command {cmd.name!r} not allowlisted (fail closed)")
        if cmd.name == "capture_now":
            receipt = self._capture_once()
            return CommandResult(ok=receipt is not None,
                                 detail="captured" if receipt else "capture failed",
                                 data={"object_id": receipt.object_id} if receipt else {})
        with self._lock:
            return CommandResult(ok=True, data={"captures_ok": self._captures_ok,
                                                "captures_failed": self._captures_failed})

    # -- internals -----------------------------------------------------------
    def _capture_once(self):
        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        try:
            frame = self._camera.capture()
            receipt = self._sink.put_blob(
                "images", frame,
                BlobMeta(content_type="image/jpeg", captured_at=now))
            with self._lock:
                self._captures_ok += 1
            self._sink.put_point("capture-metrics",
                                 TimeseriesPoint(ts=now, value=1.0,
                                                 labels={"result": "ok"}))
            return receipt
        except Backpressure:
            # declared strategy for timelapse: drop frame, count it, alert via metric
            with self._lock:
                self._captures_failed += 1
            return None
        except Exception:
            with self._lock:
                self._captures_failed += 1
            return None

    def _loop(self) -> None:
        while self._running.is_set():
            self._capture_once()
            # interruptible sleep: wakes immediately when stop() is called
            self._stop_signal.wait(timeout=self._interval_s)
