# Baseline Evaluation — TimeLapse Pro @ `eed9e3c8`

- **Reviewer:** Claude
- **Date:** 2026-07-31
- **Source:** `froekjaer/timelapse-pro`, frozen commit `eed9e3c8c67369e1924c25a11908616220c3c753` ("Extract Edge provisioning security services")
- **Purpose:** Establish the factual baseline from which the Mission Platform proposal will be designed. Claims are classified as **fact** (verified in the repo), **observation** (reviewer interpretation of facts), or **assumption** (not yet verified).

## 1. What was examined

Full clone at the frozen commit. Read in depth: `Dokumentation/00_START_HER.md` (master index), `ADR/ADR-001-platform-payload-split.md`, `ADR/ADR-0007-Evolution-from-Product-to-Platform.md`, `GO_LIVE_CHECKLIST_v10.md` (section A and decision status), `RISK_ASSESSMENT_v10.md` (structure and risk register headings), `README.md`, repository structure, CI and governance test configuration. Skimmed: `Arkitektur/Modularisering_Platform_Payload_Plan.md` (headings), documentation inventory (173 files in `Dokumentation/`). Runtime evidence was **not** available to this reviewer (no access to the live lab system); this is a limitation recorded per the authority hierarchy in `BASELINE.md`.

## 2. Quantitative facts

| Metric | Value | Source |
|---|---|---|
| Repository size (working tree) | ~50 MB | `du -sh` at baseline |
| Python LOC (headend, edge, node-agent, tests, tools) | ~95,200 | `wc -l` over `*.py` |
| TypeScript/TSX LOC (`timelapse-ui/src`) | ~27,900 | `wc -l` |
| `headend/main.py` size | **18,541 lines** | `wc -l` |
| Direct routes in `main.py` | 234 (`@app.get/post/put/delete/patch`) | grep |
| Routers included in `main.py` | 19 (`include_router`) | grep |
| Architecture ratchet baseline | `headend_main_max_lines: 18541`, `headend_main_max_direct_routes: 235` | `tests/architecture_baseline.json` |
| Headend test files | 28 (`headend/tests/test_*.py`) | find |
| Repo-level test files | 68 (`tests/test_*.py`) | find |
| Edge Python files | 73 | find |
| Documentation files in `Dokumentation/` | 173 | find |
| CI | Single workflow `.github/workflows/ci.yml` | repo |

## 3. Facts about architecture and governance

- **F-01:** ADR-001 "Platform/Payload-snit" is **Accepted (2026-07-16)** by the Mission Owner after independent convergence of two AI reviewers (Claude and Codex sessions inside the project). It defines: a platform core (identity, config/policy, OTA, telemetry, remote access, HAL, security/RBAC, storage/backup) vs. replaceable payloads; a versioned `PayloadDriver` contract plus a capability manifest; monorepo now with migration-ready package boundaries; SemVer'd contracts; six binding amendments including OS-process isolation as the enforcement boundary, separate control-plane and data-plane contracts, fail-closed capability validation against a signed allowlist, failure contracts, normative JIT/conduit remote-access control, and additive gate-driven migration. An AI domain split (payload AI vs. platform AI, shared provider adapters, calling domain owns purpose/prompts/data classification/retention/results) is part of the accepted decision.
- **F-02:** ADR-0007 "Evolution from Product to Platform" is **Proposed** (2026-07-22, after ADR-001). It states the long-term direction: platform core + mission packages (TimeLapse, WaterWorks, Maritime, Radio, Inspection, Environmental Monitoring). The numbering scheme conflicts with ADR-001 (two ADRs, non-contiguous numbers, different templates) — recorded as a governance observation (O-06).
- **F-03:** Governance gates exist **in code**: `tests/test_architecture_ratchet.py` enforces that `main.py` may not grow (lines/routes may only shrink), and `headend/tests/test_route_auth_coverage.py` sweeps route auth coverage. The master index states new endpoints must not be added to `main.py`.
- **F-04:** The go-live status at baseline is an explicit joint **No-go for Internet-facing production** (2026-06-23, reaffirmed in v10). The system is LAB/pre-production. Blockers include port/proxy migration (CrushFTP owns 21/22/80/443 on staging/prod Macs, forcing an 8443 exposure design), backup/restore evidence, GDPR (DPIA/retention/DPA), MFA/stale-credential cleanup, and camera-specific items.
- **F-05:** The risk register (RISK_ASSESSMENT_v10 + v11 addendum) is maintained and honest: R05 (compromised edge — no mTLS/disk encryption) and R09 (no off-site backup, no restore test) are open 🔴; several found-and-fixed incidents are documented, including unauthenticated `/api/siem/*` routes (R15) and cross-customer image leakage on edge reassignment (R16). The same failure class (router mounted without auth) occurred three times (SEC-001, R15, R22) — cited in ADR-001 as a forcing function.
- **F-06:** The edge is already partially modular (`edge/hal/`, `edge/config/`, `edge/tunnel/`, `edge/update/`, signed config hierarchy, signed OTA artifacts, HMAC device identity). The headend is a monolith with extraction started (`services/`, `api/`, `ai/`, separate modules for SIEM/CMDB/ITIM/redaction/compliance).
- **F-07:** Production topology: single Mac Mini headend (FastAPI/uvicorn on 127.0.0.1:8000, PostgreSQL, nginx, React UI, Ollama), Orange Pi 4 Pro + Nikon Z30 edge (one active node), SFTP image ingestion, Gemini (Vertex, EU region) + local Ollama for AI. GRC/test/risk status lives in PostgreSQL ("GRC register"), with markdown as migration source or generated report only.
- **F-08:** Development process: solo human owner + AI sessions (Claude, Codex, historically z.ai) with an explicit collaboration model, handover logs, session-boot document, and additive-only / no-hard-delete / flag-guarded change rules.

## 4. Observations (reviewer interpretation)

- **O-01 — The strategic decision is already made; the execution gap is the real subject.** ADR-001 is a genuinely strong decision document (isolation as enforcement, fail-closed, control/data-plane split, SemVer contracts). What does NOT yet exist at baseline is the corresponding code: there is no `contracts/`, no `platform/`, no `payloads/` directory; the `PayloadDriver` contract is normative prose, not an implemented, tested interface. Mission Platform's job is therefore less "invent a direction" and more "prove the direction is implementable without losing the running product".
- **O-02 — The headend monolith is the largest single migration risk.** 18.5k lines and 234 direct routes in one file, with auth regressions as a recurring failure class. ADR-001 is primarily an *edge* architecture decision; the headend-side domain split is acknowledged but much less specified. Any credible Mission Platform proposal must make the headend decomposition explicit (control plane vs. data plane vs. payload domains) rather than inheriting "P2-01 refactoring plan" as a hand-wave.
- **O-03 — Documentation is a first-class asset and a liability.** 173 files with version discipline, master index, and honest incident records is exceptional for a solo project and is itself evidence of the Mission Framework thesis. But the volume (plus Danish as primary language) creates onboarding cost and drift risk (the master index itself tracks known inconsistencies). The platform design should reduce the amount of prose that must stay true by moving invariants into enforced contracts, schemas and tests.
- **O-04 — Security posture is design-mature, evidence-immature.** Threat modelling, zone models, RBAC, signed artifacts and JIT access are designed and largely implemented; but restore-from-backup has never been evidenced, mTLS/device-CA is missing (R05, R08), and the pentest is "virtual". The gap between designed and evidenced controls is exactly what IEC 62443/CRA assessments will probe. Mission Platform should treat *evidence generation* (not more design) as the scarce resource to optimise.
- **O-05 — Constraint-driven quirks must not leak into the target architecture.** The 8443/CrushFTP port design, Mac-Mini-as-server, and LaunchDaemon service model are rational under current constraints but are host-environment accidents, not architecture. The platform contracts must be deployment-agnostic so that a Linux/container or cloud headend is a deployment choice, not a rewrite.
- **O-06 — ADR governance is young.** Two ADRs with incompatible numbering/templates (ADR-001, ADR-0007) and a "K6 ADR process" rule that lives in a risk addendum. Mission Platform should ship a single ADR convention and register from day one.
- **O-07 — The one-operator economy is the binding non-functional constraint.** Every architectural sophistication (process sandboxing, signing infrastructure, contract SemVer discipline, per-payload SBOMs) must be weighed against a single human's maintenance budget. The strongest platform design is the one whose invariants are machine-enforced (CI gates, schemas, fail-closed defaults) rather than human-vigilance-enforced.

## 5. Assumptions carried forward

- **A-08:** The GRC register (PostgreSQL) content is not accessible at baseline commit; its markdown migration sources are treated as approximate status. Runtime claims will be marked "not verified by this reviewer".
- **A-09:** The single active edge node and one lab deployment mean migration windows are cheap *today*; the design should still assume N nodes/customers for the target.
- **A-10:** The Danish-language source documentation has been read in the original; translations into English in this workspace are the reviewer's own and flagged where meaning is uncertain.

## 6. Initial risk signals for the transformation (input to the risk register)

| ID | Signal | Consequence if ignored |
|---|---|---|
| S-01 | Platform generalisation competes with production-readiness (Codex scope concern, already in ADR-001 §amendment 6) | The running product stalls; go-live blockers age while platform work absorbs sessions |
| S-02 | Contract designed before second real payload exists | `PayloadDriver` fits timelapse only; false generality discovered at first OT payload, forcing a breaking major |
| S-03 | Process isolation on Orange Pi class hardware is unproven at baseline | Isolation promise in ADR-001 amendment 1 may be unaffordable on the actual fleet; needs a measured spike, not assertion |
| S-04 | Headend decomposition underspecified relative to edge | Monolith persists behind a "platform" façade; auth-regression failure class continues |
| S-05 | Evidence debt (backup/restore, mTLS, pentest) predates the platform | Platform inherits unevidenced controls and multiplies the surface on which they are claimed |
| S-06 | Solo-operator bus factor | Any architecture that needs continuous expert attention degrades unsafely; fail-closed and machine-enforced gates are mandatory |

## 7. Position on the existing direction (preliminary)

The accepted Platform/Payload direction (ADR-001, with ADR-0007's ambition) is **examined as evidence and preliminarily judged sound in intent**: the forcing functions (monolith growth, repeated auth failure class, OT ambition) are real and documented, and the amendments show working challenge-and-correct governance. The open questions this review will pursue are not *whether* to split platform from payload, but: (1) whether the contract set (control plane, data plane, manifest) is right-sized for a one-operator economy; (2) whether the headend needs a stronger, earlier decomposition than the source plan gives it; (3) whether isolation enforcement is achievable on the actual hardware fleet; and (4) whether the migration can be staged so that timelapse delivery and go-live blockers are *accelerated*, not delayed, by the platform work. Conclusions will be recorded as ADRs in this workspace.
