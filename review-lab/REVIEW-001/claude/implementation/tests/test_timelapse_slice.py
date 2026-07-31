"""End-to-end vertical slice: admit -> configure -> run -> data lands
classified in the spool -> commands -> backpressure failure contract."""
import copy
import json

import pytest

from contracts.control import Command, CommandRejected, PayloadPolicy, PolicyRejected
from payloads.timelapse.driver import TimelapseDriver
from platform_host.supervisor import PayloadState


def factory(manifest, sink):
    return TimelapseDriver(sink)


def good_policy():
    return PayloadPolicy(revision=1, settings={"interval_s": 3600})


def test_full_capture_flow(supervisor, timelapse_manifest, tmp_path):
    supervisor.admit(timelapse_manifest, factory)
    supervisor.configure_and_start("timelapse", good_policy())
    assert supervisor.state("timelapse") is PayloadState.RUNNING

    result = supervisor.command("timelapse", Command(name="capture_now"))
    assert result.ok

    spool = tmp_path / "spool" / "timelapse"
    blobs = list(spool.glob("images-*.bin"))
    metas = list(spool.glob("images-*.meta.json"))
    assert len(blobs) >= 1 and len(metas) >= 1

    sidecar = json.loads(metas[0].read_text())
    assert sidecar["classification"] == "personal-images"       # GDPR mechanism
    assert sidecar["retention_class"] == "customer-contract"
    assert sidecar["content_type"] == "image/jpeg"
    assert blobs[0].read_bytes().startswith(b"\xff\xd8")        # actual image bytes

    points = list(spool.glob("capture-metrics-*.meta.json"))
    assert points, "telemetry point must accompany capture"
    assert json.loads(points[0].read_text())["classification"] == "operational"

    supervisor.stop("timelapse")
    assert supervisor.state("timelapse") is PayloadState.STOPPED


def test_invalid_policy_rejected_and_previous_kept(supervisor, timelapse_manifest):
    supervisor.admit(timelapse_manifest, factory)
    supervisor.configure_and_start("timelapse", good_policy())
    supervisor.stop("timelapse")
    with pytest.raises(PolicyRejected):
        supervisor.configure_and_start(
            "timelapse", PayloadPolicy(revision=2, settings={"interval_s": -5}))
    # previous good policy still in force: start again works
    supervisor.configure_and_start("timelapse", good_policy())
    supervisor.stop("timelapse")


def test_unknown_command_rejected(supervisor, timelapse_manifest):
    supervisor.admit(timelapse_manifest, factory)
    supervisor.configure_and_start("timelapse", good_policy())
    with pytest.raises(CommandRejected):
        supervisor.command("timelapse", Command(name="format_disk"))
    supervisor.stop("timelapse")


def test_backpressure_drops_frame_and_counts_it(supervisor, timelapse_manifest):
    doc = copy.deepcopy(timelapse_manifest)
    doc["quotas"]["disk_mb"] = 0  # zero disk quota -> immediate backpressure
    supervisor.admit(doc, factory)
    supervisor.configure_and_start("timelapse", good_policy())
    result = supervisor.command("timelapse", Command(name="capture_now"))
    assert not result.ok  # frame dropped per declared strategy, not crashed
    stats = supervisor.command("timelapse", Command(name="get_stats"))
    assert stats.data["captures_failed"] >= 1
    supervisor.stop("timelapse")
