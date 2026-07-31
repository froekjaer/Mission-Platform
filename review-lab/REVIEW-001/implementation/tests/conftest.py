import json
import sys
from pathlib import Path

import pytest

IMPL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(IMPL))

from contracts.manifest import Quotas  # noqa: E402
from platform_host.policy import load_verified_policy, sign_policy  # noqa: E402
from platform_host.supervisor import Supervisor, default_supported_majors  # noqa: E402

NODE_KEY = b"test-node-signing-key"


def make_policy_doc(**overrides):
    doc = {
        "node_id": "TL-TEST-NODE",
        "allowed_capabilities": ["camera.usb", "modbus.read"],
        "quota_ceilings": {"cpu_pct": 80, "mem_mb": 1024, "disk_mb": 128, "net_kbps": 0},
        "supported_contract_majors": default_supported_majors(),
    }
    doc.update(overrides)
    return doc


@pytest.fixture()
def node_policy():
    doc = make_policy_doc()
    return load_verified_policy(doc, sign_policy(doc, NODE_KEY), NODE_KEY)


@pytest.fixture()
def supervisor(node_policy, tmp_path):
    return Supervisor(node_policy, spool_root=tmp_path / "spool")


def load_manifest(name: str) -> dict:
    return json.loads((IMPL / "payloads" / name / "manifest.json").read_text())


@pytest.fixture()
def timelapse_manifest():
    return load_manifest("timelapse")


@pytest.fixture()
def waterworks_manifest():
    return load_manifest("waterworks_sim")
