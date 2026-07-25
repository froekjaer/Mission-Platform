# Risk Register — Z.ai REVIEW-001 Submission

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Severity scale:** Critical / Major / Minor / Observation (per Mission Framework `review-kit/severity-classification`)

Risks here are of two kinds: (A) risks **in the proposed architecture** that the Mission Owner must accept or treat, and (B) risks **in this submission itself** (what I did not prove). Both are explicit per the evidence standard.

---

## A. Architectural risks (the proposal)

| ID | Risk | Cause | Impact | Severity | Owner | Treatment |
|----|------|-------|--------|----------|-------|-----------|
| R-Z-01 | The contract becomes a change bottleneck | SemVer discipline on `contracts/` makes every breaking change a coordinated platform+payload effort | Slower evolution; payload authors blocked on platform releases | Major | Platform owner | Keep contract minimal (lifecycle + manifest only); push domain concerns into payload-owned code; document the compatibility matrix as a contract, not a convention |
| R-Z-02 | Isolation primitive (systemd+seccomp) insufficient for a future threat | seccomp filters can be bypassed by kernel vulns; AppArmor optional | A payload compromise escapes containment | Major (conditional on Q-7 third-party payloads) | Platform owner + Mission Owner | Start first-party-only (Q-7 default); escalate to containers/microVMs before admitting third-party payloads; this is exactly why ADR-Z-002 is reversible |
| R-Z-03 | Manifest authoring errors block legitimate payloads | A payload developer under-specifies the allowlist; legitimate operation is denied fail-closed | A working payload appears broken; support load | Minor | Payload authors | Per-payload manifest CI test (K7); clear denial logging; a staging environment to discover mismatches before prod |
| R-Z-04 | Monolith decomposition introduces a route-auth regression during Step 3 | The exact failure class (SEC-001/R15/R22) recurring during extraction | An unauthenticated endpoint reaches prod | Major | Platform owner | K1 route-auth sweep at every commit; K3 ratchet; this is the ratchet's reason for existing |
| R-Z-05 | Two-orchestrator coexistence drifts during Step 2 | Old `edge/agent.py` and new `platform/supervisor` run in parallel behind a flag | Inconsistent behaviour; hard-to-diagnose incidents | Minor | Platform owner | Parity tests; cutover gate; old orchestrator quarantined (not deleted) per project principle |
| R-Z-06 | The platform assumes one headend | Federation is deferred (ADR-001); a second region/headend is not designed | Multi-region impossible without another ADR | Observation (correctly deferred) | Mission Owner | Accept; revisit when a second region is on the horizon (ADR-001 deferral) |
| R-Z-07 | The 11 🔴 production blockers are not addressed by this architecture | This submission enables them (gives them a home) but does not complete them | Production-readiness timeline unaffected by architecture alone | Major (existing, inherited) | Mission Owner + productionisation track | Catalogued in §B below; the architecture is necessary but not sufficient for go-live |
| R-Z-08 | Bias: I authored the REVIEW-001 governance in BUILD-016 | I know the rubric in detail | Submission "teaches to the test"; architecture shaped by criteria not just need | Minor | Mission Owner (meta-review) | Every decision traced to TimeLapse Pro evidence with Why/Because/For-whom; bias note in every major doc; meta-review can discount |

---

## B. Inherited production blockers (NOT solved by this submission)

These come from `KRAVREGISTER_og_STATUS_v10.md`. The architecture gives each a clean home but does not implement them. Listed for traceability so the meta-review sees I have not silently ignored them.

| Source ID | Blocker | Architectural home (where it lands in Mission Platform) | Status carried forward |
|-----------|---------|----------------------------------------------------------|------------------------|
| SEC-009 | Intern CA + client-certs (mTLS) | `platform/identity/` | 🔴 Designed (`Claude_Intern_CA_mTLS_Design_2026-07-05.md`), not coded |
| SEC-010 | Disk encryption on edge | `platform/` (node hardening) | 🔴 Requires physical access (P2-07) |
| SEC-012 | GDPR DPIA + retention + DPA | `payloads/*/manifest.yaml` `data_classification` feeds it | 🟡 Template ready, not legally approved |
| UI-010 | Redaction workflow | `payloads/timelapse/` (image-domain) | 🔴 Missing |
| PROV-004/005 | Cold/warm headend backup + restore evidence | `platform/storage/` | 🔴 Architecture not designed; restore-test open (R09) |
| CFG-007/008/009 | GPS sync, web terminal, local mgmt UI | `platform/` + payload UI | 🔴 Missing |
| SEC-011 | fail2ban | `platform/` (headend hardening) | 🟡 Config ready, manual setup |
| UPD-006/007 | Signed change tickets + MFA approval | `platform/update/` | 🟡 Partial |

These belong to the productionisation track (Sprints H–N in `KRAVREGISTER` §4), not the architecture proof. The architecture *unblocks* them; it does not *complete* them.

---

## C. Submission risks (what I did NOT prove)

Honest limitations of this submission, per the evidence standard's "absence of evidence is not evidence of absence."

| ID | Limitation | Why it exists | What would close it |
|----|-----------|---------------|---------------------|
| L-01 | The vertical slice uses a `SyntheticCapture`, not a real Nikon Z30 via gphoto2 | No hardware in this environment | Run the contract spike on a real edge node (Migration Step 0 on hardware) |
| L-02 | The `Sandbox` is an in-process proxy, not a real systemd service + seccomp filter | No root/systemd in this environment | Implement the unit generator; run the capability-enforcement test on a real Armbian node |
| L-03 | No real database; multi-tenant row-level isolation is argued, not tested against PostgreSQL RLS | Out of slice scope | A dedicated Confidentiality test against PostgreSQL RLS in Step 4 |
| L-04 | I did not read every line of `headend/main.py` (783 KB) | Time/scope; read tree + structure + 234-route count + first 80 lines + the partial routers | A line-level audit during Step 3 extraction (the ratchet enforces it then) |
| L-05 | The second payload is a stub, not a real waterworks/sensor payload | The point was to prove Extensibility, not build a vertical | A real second vertical when one is on the horizon (ADR-0007 trigger) |
| L-06 | No load/performance evidence | Performance is *Low* priority (SABSA F1); not load-bearing for the architectural argument | Load test if/when a payload's manifest quota proves insufficient |

---

## D. Assumptions (recap from ASSUMPTIONS_AND_QUESTIONS.md)

The seven open questions (Q-1 to Q-7) each carry a default I proceeded on. If the Mission Owner reverses any default, the affected ADRs/risks change:

- **Q-4** (isolation primitive) → directly affects R-Z-02 and ADR-Z-002.
- **Q-7** (third-party payloads) → directly affects R-Z-02 severity (could escalate Major→Critical).
- **Q-1** (repo model) → affects contract packaging but not the architecture.

All other assumptions (A/B/C) are low-risk and reversible.
