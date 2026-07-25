# Business Architecture (SABSA Contextual + Business layers)

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Source evidence:** `timelapse-pro@eed9e3c8` — `SABSA_Architecture_v10.md`, `KRAVREGISTER_og_STATUS_v10.md`, `ADR-001`, `ADR-0007`, `00_START_HER.md`, `Startkrav.docx` (founding brief, quoted in KRAVREGISTER §6).

This is SABSA layer 1–2: *why the platform exists* and *what business attributes it must deliver*. Every lower layer (conceptual → operational) traces here. It derives from the TimeLapse Pro evidence; where it generalises to the Mission Platform, that generalisation is explicit and justified.

---

## 1. Mission

> **Deliver trustworthy, autonomous edge intelligence and recording for small-to-mid Danish OT and site-monitoring installations — starting with authenticated construction timelapse — through a modular platform where each mission capability is a swappable payload, and where the platform's job is to make every payload safe, observable, updatable, and accountable.**

Three things in that sentence are load-bearing and *different* from the TimeLapse Pro mission:

| TimeLapse Pro mission | Mission Platform generalisation | Why the change |
|---|---|---|
| "timelapse recordings from unmanned locations" | "edge intelligence and recording for OT/site-monitoring" | ADR-0007: timelapse is the first payload, not the boundary |
| "central management of cameras" | "modular platform with swappable payloads" | ADR-001 §1: the functional core must be replaceable |
| (single product) | "make every payload safe, observable, updatable, accountable" | ADR-001 §2 + amendments: the platform owns non-functional guarantees |

The platform's reason for existing is **the non-functional guarantees it gives to any payload**. That is the business value proposition.

---

## 2. Stakeholders and their needs

| Stakeholder | Need | Priority | Evidence |
|---|---|---|---|
| **Mission Owner (Peter Frøkjær)** | A credible path from a timelapse product to a reusable, open-sourceable secure OT platform without abandoning the paying timelapse customers. | Critical | ADR-0007 vision; ADR-001 §Afgrænsning "long-term vision… open-source a secure platform for smaller OT installations" |
| **End customers (construction site owners, e.g. Kirkbi/Travbyen)** | Reliable, legally-defensible documentation of construction progress; their data isolated from other tenants; clear retention. | Critical | SABSA contextual: "ubestrideligt juridisk bevis"; KRAVREGISTER SEC-012 (DPA with Kirkbi) |
| **Site managers / operators** | Capture keeps running through network/power failure; remote config without a site visit; time-synchronised multi-camera capture. | Critical | SABSA Availability/Continuity/Synchronicity (all KRITISK) |
| **Future payload owners (waterworks, energy, maritime, environmental)** | A documented contract they can build against without reading the platform internals; confidence their payload cannot compromise or be compromised by others. | High (architectural test case now) | ADR-001 §1 "vandværk, vindmølle, solcelle"; invitation future-payload list |
| **Compliance / audit function** | Demonstrable, per-payload evidence for GDPR, CRA, NIS2, IEC 62443. | High | KRAVREGISTER SEC-001; SABSA Accountability |
| **Support / on-call engineers** | Safe remote access to an edge or its OT backend without opening inbound ports; JIT, logged, revocable, kill-switchable. | High | ADR-001 amendment 5; RISK_ASSESSMENT R19 |
| **Regulators / data subjects** | Lawful processing (DPIA, DPA, breach procedure); data minimisation and retention enforcement. | High | KRAVREGISTER SEC-012, UI-010; GDPR Art. 33/34 |
| **Reviewers / meta-review (Mission Framework)** | A submission that can be compared blind against alternatives, with dissent preserved. | Process | REVIEW-001 invitation |

### "For whom" — proportionality test

The platform must deliver capability **proportionate to need**. A construction timelapse site and a waterworks SCADA edge have different consequence profiles. The architecture answers this with **per-payload capability manifests and data classification** (ADR-001 §2): the waterworks payload declares industrial-process data with strict retention; the timelapse payload declares image data with its own retention. The platform enforces both, but differently. This is the SABSA "For whom?" answer made concrete.

---

## 3. Business attributes (SABSA F1) — inherited and extended

TimeLapse Pro defines 10 business attributes (`SABSA_Architecture_v10.md` §2). The Mission Platform inherits all 10 **unchanged for the timelapse payload**, and adds 3 that the platform generalisation makes first-class. Priorities follow the source.

### Inherited (per-payload, must not regress)

| Attribute | Definition | Why load-bearing | Platform realisation |
|---|---|---|---|
| **Integrity** | Images unchanged lens-to-archive (legal evidence) | Critical — the commercial promise | SHA-256 sidecar JSON; SFTP verification. *Platform responsibility:* the integrity guarantee is a platform service available to any payload that declares its data as evidence-grade. |
| **Availability** | Capture >99% of scheduled time, network-independent | Critical | Store-and-forward 50 GB buffer; nightly reboot; watchdog. *Platform responsibility:* the autonomy runtime is platform-owned. |
| **Synchronicity** | Site cameras capture within 1 s | Critical | NTP/chrony. *Platform responsibility:* time authority is platform infrastructure. |
| **Confidentiality** | Tenant A can never read Tenant B | High | `customer_id` row-level filtering; JWT RBAC. *Platform responsibility:* multi-tenancy is platform-core, not payload. |
| **Accountability** | Every action traceable to user+time | High | Audit log; per-capture heartbeat diagnostics. *Platform responsibility:* the audit spine is platform-owned. |
| **Continuity** | Boot-to-capture < 120 s | High | gvfs disabled; sysfs GPIO. *Platform responsibility:* boot ordering and payload start dependencies are managed by the platform. |
| **Resilience** | Survives network/power/device failure | High | Circular buffer; store-and-forward; modem power-cycle. *Platform responsibility:* the buffer/quarantine abstraction is platform-owned. |
| **Manageability** | Remote config without site visit | Medium | Web UI config hierarchy; CI/CD self-update. *Platform responsibility:* the config/policy hierarchy and update authority are platform-core. |
| **Scalability** | Designed for 500–1000 edges, 100+ sites | Medium | Multi-tenant RBAC; PostgreSQL. *Platform responsibility:* shared. |
| **Performance** | 1 image/day → 1/min, configurable | Low | FFmpeg; filters; day/night selection. *Payload responsibility:* throughput characteristics are payload-defined via manifest quota. |

### Added by the platform generalisation (new, first-class)

| Attribute | Definition | Why it becomes first-class | Realisation |
|---|---|---|---|
| **Extensibility** | A new payload can be added without touching platform internals or other payloads | This *is* the mission of the platform | Versioned PayloadDriver contract + capability manifest + isolation boundary. Inheritable ADR-001 positive consequence. |
| **Payload isolation / fault containment** | A fault in one payload cannot compromise the platform core or another payload | Without this, OT verticals are unsafe (IEC 62443, CRA) | Separate OS-sandboxed process per payload; fail-closed capability enforcement (ADR-001 amendments 1 & 3). |
| **Proportionate compliance** | Each payload carries its own data classification, retention, and regulatory mapping | Different verticals have wildly different data classes (image vs. process data) | Data-classification field in the capability manifest drives per-payload DPIA/retention (ADR-001 §6, GDPR consequence). |

---

## 4. Business attributes → measurable success criteria

Vague attributes are untestable. Each critical/high attribute gets a measurable criterion the meta-review can check.

| Attribute | Measurable success criterion |
|---|---|
| Integrity | A payload that declares evidence-grade data has its artifact hash verified end-to-end; a tampered artifact is rejected and logged. Contract test demonstrates this. |
| Availability | The edge autonomy runtime continues to capture/store-and-forward when the headend is unreachable; demonstrated by a test that disconnects the headend and verifies buffer behaviour. |
| Synchronicity | Platform exposes a time-authority service payloads can consume; documented NTP/chrony contract. |
| Confidentiality | Multi-tenant row-level isolation is enforced at the platform data layer, not re-implemented per payload; a payload cannot construct a query that crosses tenants. |
| Accountability | Every platform-mediated action (config change, capability grant, payload command, access ticket) emits an audit record with actor, time, and traceable reason. |
| Extensibility | A second (stub) payload can be added by implementing the contract *only* — no platform code changes — and is loaded and isolated. Demonstrated in the vertical slice. |
| Payload isolation | A payload that attempts an undeclared capability (e.g. an off-manifest network destination) is denied fail-closed, and the attempt is logged. Contract test demonstrates this. |
| Proportionate compliance | The capability manifest schema requires a `data_classification` field; a payload without it fails to load. |

---

## 5. Trust model summary (contextual)

Inherited and sharpened from `SABSA_Architecture_v10.md` §3 and ADR-001 amendment 5:

- **Edge is untrusted by default.** A payload on the edge is *less* trusted than the platform core on the edge — it runs in its own process with capabilities granted by platform policy, not self-assumed.
- **The contract is the only trust path between platform and payload.** No implicit memory/shared-credential trust (this is precisely what amendment 1 fixes).
- **Remote access to a payload or its OT backend always traverses a platform JIT conduit** — short-lived identity, destination allowlist, session recording, kill switch. Never an inbound port on the OT network.
- **Environment is a trust boundary now** (`rd`/`staging`/`prod`), not at cutover — per the SABSA §3 note that the prod host already runs CrushFTP with live customer data. Default-deny agent access to staging/prod; break-glass is a designed, logged exception, not a gap.

Detailed zone/conduit mapping is in the Conceptual Architecture.

---

## 6. Why / Because / For whom — the platform's existence justification

**Why does the Mission Platform exist?**
Because TimeLapse Pro's own architecture (ADR-001, ADR-0007) declares that timelapse is one payload among future many, and that the non-functional core (identity, config, OTA, telemetry, remote access, HAL, security, storage) must be reusable.

**Because?**
Because (a) the alternative — forking the whole codebase per vertical — was explicitly rejected in ADR-001 as unacceptable for OT and CRA/IEC 62443; (b) the monolith's repeated route-auth failures (SEC-001, R15, R22) show that without an enforced boundary the debt keeps regenerating; (c) the edge is *already* half-modular (HAL, camera drivers, capture, tunnel, update, upload) — the platform/payload split formalises a direction the code already half-follows.

**For whom?**
For the Mission Owner (open-source OT-platform vision), for paying timelapse customers (who must not lose the evidence/integrity promise), for future payload owners (who need a contract to build against), and for regulators/data subjects (who need per-payload demonstrable compliance). The capability is delivered proportionate to consequence: a timelapse edge and a waterworks edge share the platform but carry different manifests, data classes, and isolation profiles.

---

## 7. Out of scope at this layer

- Specific technology choices (Postgres vs. other, FastAPI vs. other) → Logical/Physical layers.
- Isolation primitive (systemd+seccomp vs. alternatives) → ADR-Z-002, deferred to Q-4.
- Migration sequence → Migration strategy.
- Multi-vendor payload trust → future ADR (per ADR-001 deferral).
