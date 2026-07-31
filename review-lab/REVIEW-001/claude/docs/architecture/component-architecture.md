# Component Architecture (SABSA Component Layer) & Target Repository Structure

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Target repository structure (monorepo, package-boundary-enforced)

Monorepo retained (source ADR-001 model A) — right for a one-operator economy; boundaries are package boundaries enforced by CI, so model B (published platform package) stays cheap.

```
mission-platform/
  contracts/                    # THE seam. No dependencies on anything else.
    control/payload_driver.py   #   PayloadDriver ABC + lifecycle types (SemVer)
    data/data_channel.py        #   DataChannel/DataSink ABCs + classification enums
    manifest/schema/manifest-v1.schema.json
    manifest/loader.py          #   parse + validate (fail closed)
    CHANGELOG.md                #   contract SemVer history
  platform/
    edge_agent/                 # identity, policy sync, OTA, heartbeat, forwarder
      supervisor/               #   payload lifecycle + manifest enforcement
    headend/
      control_api/              # enrollment, config+signing, OTA, RBAC, tickets, GRC
      data_plane/               # ingestion, storage registry, retention, backup, SIEM pipe
      common/                   # authenticated router factory, db, settings
    security/                   # signing, token, allowlist policy tools
  payloads/
    timelapse/
      edge/                     # TimelapseDriver (camera HAL grant, capture loop, QA)
      headend/                  # tagging, video build, site look — mounted as domain service
      manifest.yaml
    _reference/waterworks_sim/  # anti-coupling test payload (simulated), never shipped
  experience/ui/                # React UI (admin + customer)
  deployments/
    profile-a/                  # launchd + systemd units, nginx, install scripts
    profile-b/                  # Linux/container compose
  tests/
    architecture/               # import-boundary, route-auth, ratchet, second-payload smoke
  tooling/                      # generators, SBOM, evidence collectors
  docs/  adr/
```

## 2. Component rules (machine-enforced)

1. `contracts/` imports nothing from `platform/` or `payloads/` (pure).
2. `platform/` never imports `payloads/` — **the** anti-coupling invariant (CI: `tests/architecture/test_import_boundaries.py`).
3. `payloads/*` import `contracts/` only (not `platform/`); headend payload services get platform access via dependency injection of contract interfaces.
4. Every HTTP router is created via `platform/headend/common/secure_router.py` (auth required by construction); CI greps direct `APIRouter()` instantiation outside the factory.
5. `main.py` (composition root) may only mount and configure — line/route ratchet inherited from source and re-pointed at composition-only target.
6. Every `DataChannel` declared in a manifest must carry classification + retention class — schema-enforced.

## 3. Key components and their source lineage

| Component | Builds on source element | Mode |
|---|---|---|
| edge_agent core | `edge/agent.py`, `edge/config`, `edge/update`, `edge/tunnel` | Adapted (split agent from payload) |
| supervisor | — (new; normative in source ADR-001 amendment 1) | New |
| contracts | source ADR-001 normative sketch | New (formalisation) |
| control_api | `headend/main.py` auth/RBAC/config/OTA routes + `api/` routers | Rewritten-in-place via strangler |
| data_plane | SFTP ingest, `storage_registry.py`, `backup_integrity.py`, `siem.py` | Adapted |
| timelapse payload edge | `edge/camera`, `edge/capture`, `edge/hal` camera parts, edge QA | Adapted behind PayloadDriver |
| timelapse payload headend | AI tagging, video, site look modules | Adapted behind domain service |
| GRC register | PostgreSQL GRC schema | Reused |
| UI | `timelapse-ui/` | Reused, restructured by service later |

Full mapping: `migration/traceability.md`.

## 4. Interfaces (component level, v1)

```python
# contracts/control/payload_driver.py  (v1.0)
class PayloadDriver(ABC):
    def configure(self, policy: PayloadPolicy) -> None: ...
    def start(self) -> None: ...
    def stop(self, deadline_s: float) -> None: ...
    def health(self) -> HealthReport: ...          # status, detail, metrics
    def handle_command(self, cmd: Command) -> CommandResult: ...

# contracts/data/data_channel.py  (v1.0)
class DataSink(ABC):                               # provided BY platform TO payload
    def put_blob(self, channel: str, payload: bytes, meta: BlobMeta) -> PutReceipt: ...
    def put_point(self, channel: str, point: TimeseriesPoint) -> PutReceipt: ...
    def put_event(self, channel: str, event: Event) -> PutReceipt: ...
```

Failure contracts (per source ADR-001 amendment 4): `configure` invalid ⇒ raise `PolicyRejected`, supervisor keeps previous policy; `health` timeout ⇒ supervisor restart with backoff, then rollback payload version, then mark mission degraded (alert); `put_*` when spool full ⇒ `Backpressure` with retry-after — payload must drop-or-buffer per its manifest-declared strategy; contract-major mismatch ⇒ refuse start. All transitions logged as structured audit events.

## 5. The manifest (v1) — abbreviated

```yaml
manifest_version: 1
payload: {name: timelapse, version: 1.0.0}
contracts: {control: "1.x", data: "1.x"}
capabilities: [camera.usb]              # unknown value ⇒ refuse (fail closed)
quotas: {cpu_pct: 50, mem_mb: 512, disk_mb: 4096, net_kbps: 0}   # 0 = no direct net
filesystem: {readwrite: [/var/spool/mission/timelapse]}
channels:
  - {name: images, kind: blob, classification: personal-images, retention_class: customer-contract}
  - {name: capture-metrics, kind: timeseries, classification: operational, retention_class: ops-1y}
```

Validation: JSON Schema (structure, unknown-field rejection) + policy check against the operator-signed allowlist (which capabilities/quota ceilings this node may grant). Both fail closed. Implemented and test-evidenced in the vertical slice (`implementation/`).
