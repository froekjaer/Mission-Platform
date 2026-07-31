# Business & Stakeholder Architecture (SABSA Contextual Layer)

- **Reviewer:** Claude · **Date:** 2026-07-31 · **Status:** Submitted for REVIEW-001

## 1. Mission

> Operate long-lived, unattended edge installations that capture domain data reliably and securely for years, deliver it to customers as a finished product, and do so with a total operating effort affordable to a one-person business.

Timelapse photography is the first realisation: cameras at construction sites and landscapes producing images for years, turned into curated archives and videos. The mission is **not** "run cameras"; it is "run trustworthy unattended edge missions". That reframing is what makes waterworks, energy, maritime, environmental and SDR payloads architectural test cases rather than fantasies.

**Why?** The owner's stated ambition (source ADR-001, ADR-0007) and the invitation's platform vision. **Because?** The non-functional capabilities (identity, config, OTA, telemetry, remote access, storage) already dominate the source codebase and are domain-independent; the domain code is a minority. **For whom?** The Mission Owner (business viability), customers (a working product), and future OT operators (a safe platform).

## 2. Stakeholders and their needs

| Stakeholder | Need | Consequence of failure |
|---|---|---|
| Mission Owner / operator (Peter) | Operate the fleet and business alone, bounded daily effort; sell outcomes, not maintenance | Business is not viable; burnout; unsafe shortcuts |
| Customers (site owners) | Reliable capture, access to their images/videos only, predictable delivery, GDPR-clean handling | Churn, liability, reputational damage |
| Data subjects (people on images) | Privacy: minimal capture of persons, lawful basis, retention limits, redaction | GDPR breach, complaints, fines |
| Edge site host (provides power/net/mount) | Non-intrusive device, no risk to their network | Device removed; site lost |
| Future OT customers (waterworks etc.) | Safe monitoring that cannot endanger the process; sovereignty over their data | Physical/safety consequences; regulatory exclusion |
| AI collaborators (Claude/Codex sessions) | Machine-readable invariants, enforced gates, honest docs | Silent drift, repeated failure classes |
| Regulators (GDPR, CRA, NIS2, AI Act) | Demonstrable compliance evidence | Market access blocked; penalties |
| Future contributors / auditors (if open-sourced) | Understandable, governable architecture with clean IP | Vision dies with the sole author |

## 3. Business attribute profile

SABSA business attributes chosen for the platform (target values are the measurable success criteria; "evidenced" means machine-produced evidence, not prose claims):

| Attribute | Definition here | Measurable target |
|---|---|---|
| **Operable-by-one** | Routine operation of platform + all payloads within a solo operator's budget | ≤ 30 min/day routine operations across the fleet; every routine task has a runbook or is automated |
| **Unattended-reliable** | Edge nodes capture and deliver without site visits | ≥ 99% scheduled capture success per node per month; site visits only for hardware failure |
| **Fail-closed-secure** | Absence of configuration/policy denies; privileges never default open | 100% of routes authenticated by sweep test; unknown manifest capability ⇒ payload refused to start (test-evidenced) |
| **Recoverable** | Any single hardware loss (edge node or headend) is recoverable from evidence-tested backups | Restore test performed and evidenced per release cycle; RPO ≤ 24 h, RTO ≤ 1 working day |
| **Payload-neutral** | Platform core contains zero payload-domain concepts | CI test: platform packages import no payload packages; second-payload smoke test passes without platform change |
| **Traceable** | Every material decision and migrated element traceable to evidence | ADR register complete; source-to-target map covers 100% of migrated components |
| **Privacy-respecting** | Data classification drives retention/deletion per payload | Every data-plane stream declares classification; retention jobs evidenced; DPIA per camera-bearing deployment |
| **Compliance-ready** | CRA/NIS2/IEC 62443 posture demonstrable when required | SBOM per release; vulnerability handling process documented; zone/conduit model current |
| **Evolvable** | New payloads and deployment targets without core rewrite | New payload requires only contract implementation + manifest; headend deployable on macOS and Linux |

## 4. Necessary value vs. optional sophistication

Judgement applied throughout this submission (per the invitation's proportionality principle):

**Necessary now:** fail-closed contracts, route-auth enforcement, restore evidence, data classification, headend decomposition by plane, one enforced ADR convention, second-payload anti-coupling test.

**Necessary before OT payloads, not before:** OS-level payload sandboxing on the fleet, mTLS/device CA, signed payload packages, per-payload SBOM/VEX, conduit session recording.

**Optional sophistication (rejected for now, recorded):** microservices/multi-repo, Kubernetes, event bus/message broker as mandatory backbone, multi-headend federation, payload marketplace/multi-vendor trust (source ADR-001 already defers this), bespoke plugin DSLs.

**Because?** Each "necessary now" item closes a documented failure class or go-live blocker in the source evidence (baseline-evaluation.md F-03, F-04, F-05). Each deferred item's cost lands on a single operator (O-07) before any second payload pays for it.

## 5. Capability allocation (need, consequence, cost, sovereignty, accountability)

| Capability | Allocated to | Why there |
|---|---|---|
| Capture/domain logic | Payload, on edge | Consequence local to mission; domain expertise pluggable |
| Identity, enrollment, OTA, telemetry | Platform, edge+headend | Same for every mission; highest blast radius ⇒ one hardened implementation |
| AI on images (tagging, QA) | Timelapse payload (calling-domain ownership) | Purpose, prompts, classification, results owned by the domain — retained from source AI domain split |
| AI for operations (SIEM triage, docs) | Platform | Serves the operator, not a customer domain |
| Data storage & retention | Platform mechanism, payload policy | Platform enforces; payload declares classification/retention need |
| Remote access to sites/OT | Platform JIT conduits only | Sovereignty and accountability demand one audited path |
| Final authority | Mission Owner (human) | Accountability cannot be delegated to AI; per Mission Framework |

## 6. Explicit non-goals

- Replacing the running TimeLapse Pro lab system before a separately approved migration (per BASELINE.md preservation clause).
- Building a general IoT cloud product for external developers during REVIEW-001.
- Achieving formal IEC 62443 certification now; the target is *credible alignment* with evidence hooks in place.
