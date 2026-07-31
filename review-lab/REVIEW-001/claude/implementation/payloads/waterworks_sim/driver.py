"""Waterworks simulator — the anti-coupling proof payload (never shipped).

Purpose (ADR-CL-002 refinement 3): a permanently maintained second payload
from a DIFFERENT domain (OT monitoring: timeseries + events, no imagery,
no camera). If the platform ever grows a timelapse assumption, this payload's
tests break. Imports ONLY from contracts.
"""
from __future__ import annotations

import datetime as _dt

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
from contracts.data import DataSink, Event, TimeseriesPoint


class WaterworksSimDriver(PayloadDriver):
    """Simulated flow sensor with a high-flow alarm. Monitoring-only:
    no actuation exists in contract v1 by design (safety gate)."""

    ALLOWED_COMMANDS = {"read_now"}

    def __init__(self, sink: DataSink) -> None:
        self._sink = sink
        self._alarm_threshold: float | None = None
        self._running = False
        self._reads = 0
        self._flow = 10.0

    def configure(self, policy: PayloadPolicy) -> None:
        threshold = policy.settings.get("alarm_threshold_m3h")
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise PolicyRejected("alarm_threshold_m3h must be positive")
        self._alarm_threshold = float(threshold)

    def start(self) -> None:
        if self._alarm_threshold is None:
            raise PolicyRejected("start() before configure() (fail closed)")
        self._running = True

    def stop(self, deadline_s: float) -> None:
        self._running = False

    def health(self) -> HealthReport:
        status = HealthStatus.OK if self._running else HealthStatus.DEGRADED
        return HealthReport(status=status, metrics={"reads": self._reads})

    def handle_command(self, cmd: Command) -> CommandResult:
        if cmd.name not in self.ALLOWED_COMMANDS:
            raise CommandRejected(f"command {cmd.name!r} not allowlisted (fail closed)")
        value = self.read_sensor()
        return CommandResult(ok=True, data={"flow_m3h": value})

    # -- domain --------------------------------------------------------------
    def read_sensor(self, value: float | None = None) -> float:
        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        flow = self._flow if value is None else value
        self._reads += 1
        self._sink.put_point("flow", TimeseriesPoint(ts=now, value=flow,
                                                     labels={"unit": "m3h"}))
        assert self._alarm_threshold is not None
        if flow > self._alarm_threshold:
            self._sink.put_event("alarms", Event(ts=now, kind="high-flow",
                                                 detail={"flow_m3h": flow}))
        return flow
