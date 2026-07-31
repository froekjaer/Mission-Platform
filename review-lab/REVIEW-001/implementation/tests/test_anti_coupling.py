"""Platform-neutrality proof (ADR-CL-002 refinement 3).

1. A second payload from a different domain (OT monitoring) runs under the
   SAME supervisor with ZERO platform changes.
2. Import-boundary rules are machine-checked over the actual source files:
   contracts imports nothing; platform never imports payloads; payloads
   never import platform internals.
3. Failure containment: quarantining one payload leaves the other running.
"""
import ast
import json
from pathlib import Path

from contracts.control import Command, HealthReport, HealthStatus, PayloadPolicy
from payloads.timelapse.driver import TimelapseDriver
from payloads.waterworks_sim.driver import WaterworksSimDriver
from platform_host.supervisor import PayloadState, Supervisor

IMPL = Path(__file__).resolve().parent.parent


def _imports_of(package_dir: str) -> set[str]:
    roots = set()
    for py in (IMPL / package_dir).rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


def test_contracts_package_is_pure():
    assert not {"platform_host", "payloads"} & _imports_of("contracts")


def test_platform_never_imports_payloads():
    assert "payloads" not in _imports_of("platform_host")


def test_payloads_import_contracts_only():
    for payload in ("payloads/timelapse", "payloads/waterworks_sim"):
        assert "platform_host" not in _imports_of(payload)


def test_second_domain_payload_runs_unmodified(supervisor, waterworks_manifest, tmp_path):
    supervisor.admit(waterworks_manifest, lambda m, s: WaterworksSimDriver(s))
    supervisor.configure_and_start(
        "waterworks_sim", PayloadPolicy(revision=1, settings={"alarm_threshold_m3h": 50.0}))

    result = supervisor.command("waterworks_sim", Command(name="read_now"))
    assert result.ok and "flow_m3h" in result.data

    driver_view = supervisor._payloads["waterworks_sim"].driver
    driver_view.read_sensor(value=99.0)  # exceeds threshold -> alarm event

    spool = tmp_path / "spool" / "waterworks_sim"
    assert list(spool.glob("flow-*.meta.json")), "timeseries landed"
    alarms = list(spool.glob("alarms-*.event.json"))
    assert alarms, "alarm event landed"
    assert json.loads(alarms[0].read_text())["kind"] == "high-flow"
    # and no imagery concepts anywhere in this payload's spool
    assert not list(spool.glob("images-*"))
    supervisor.stop("waterworks_sim")


def test_failure_containment_between_payloads(node_policy, tmp_path,
                                              timelapse_manifest, waterworks_manifest):
    sup = Supervisor(node_policy, spool_root=tmp_path / "spool")

    class SickDriver(WaterworksSimDriver):
        def health(self) -> HealthReport:
            return HealthReport(status=HealthStatus.FAILED, detail="simulated crash-loop")

    sup.admit(timelapse_manifest, lambda m, s: TimelapseDriver(s))
    sup.admit(waterworks_manifest, lambda m, s: SickDriver(s))
    sup.configure_and_start("timelapse", PayloadPolicy(1, {"interval_s": 3600}))
    sup.configure_and_start("waterworks_sim", PayloadPolicy(1, {"alarm_threshold_m3h": 50.0}))

    for _ in range(Supervisor.MAX_RESTARTS + 1):
        sup.health_check("waterworks_sim")

    assert sup.state("waterworks_sim") is PayloadState.QUARANTINED
    assert sup.state("timelapse") is PayloadState.RUNNING  # containment
    assert sup.health_check("timelapse") is PayloadState.RUNNING
    sup.stop("timelapse")
