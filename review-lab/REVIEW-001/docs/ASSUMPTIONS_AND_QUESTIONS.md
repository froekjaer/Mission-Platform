# Assumptions and Open Questions

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Date:** 2026-07-25
**Status:** Recorded before design, per WORKSPACE.md "Record initial assumptions and questions before designing."

This document records the assumptions I am making and the questions I cannot answer from the frozen baseline alone. Per the evidence standard, assumptions that affect findings or decisions are treated as explicit uncertainty, not as facts.

---

## A. Scope assumptions

**A-1.** The "Mission Platform" target is a *modular edge + headend platform* whose first payload is timelapse, derived from but not bound to TimeLapse Pro. I assume the platform must remain able to deliver the existing timelapse use case (ADR-001 §1: "timelapse becomes the first functional payload").

**A-2.** I assume this review is a *design and proof* exercise, not a full re-implementation of 82 requirements. The invitation requires a "functional timelapse vertical slice or credible executable proof," so I will produce a vertical slice that proves the platform/payload contract, not a feature-complete clone.

**A-3.** I assume the target language/runtime stays **Python (FastAPI) + PostgreSQL + React/TypeScript** for the headend and **Python** for the edge. Switching runtimes would add risk without serving the mission, and the skill base is Python. (Challengeable — see Q-3.)

**A-4.** I assume **one production headend** for the foreseeable future (the invitation lists future payloads, not future regions). Multi-headend federation is out of scope per ADR-001's explicit deferral ("Federation / flere prod-headends → senere ADR").

---

## B. Evidence-confidence assumptions

**B-1.** The frozen baseline commit `eed9e3c8c67369e1924c25a11908616220c3c753` is the authoritative source. I have read the v10 documentation set, both ADRs, the requirements register, and the code tree. I have *not* read every line of the ~18,000-line `main.py`. Confidence in the *architecture* is high; confidence in *implementation details* of any specific route is medium.

**B-2.** The requirements register (KRAVREGISTER) self-reports 51% implemented / 35% partial / 13% missing. The document itself notes a history of recount errors (periodic checks #25–#61). I treat the **category-level** picture as reliable evidence of where the system is mature vs. immature, but I do not rely on exact percentages.

**B-3.** ADR-001's six amendments are *accepted* (Peter, 2026-07-16) but several describe a *target* state ("platform-policy is authoritative enforcement," "separate control/data-plane contracts") that the current code has not yet reached. I treat the amendments as **binding intent**, not as implemented capability. This is the central gap my architecture must close.

---

## C. Business-context assumptions

**C-1.** The mission owner's commercial horizon is **small-to-mid Danish OT installations** (waterworks, solar, wind, maritime monitoring, environmental sensing) plus timelapse for construction. I infer this from ADR-0007's mission-package list and ADR-001's vertical examples. I am *not* assuming hyperscale or global deployment.

**C-2.** "Authenticated recordings as undisputed legal evidence" (SABSA contextual layer) remains a first-class business attribute. I assume any platform redesign must *strengthen*, not weaken, the SHA-256 lens-to-archive integrity chain.

**C-3.** I assume **GDPR, CRA, NIS2, IEC 62443, ISO 27001** are all in-scope compliance frames (they are named as core competencies and in the requirements register). The redesign should make compliance *demonstrable per payload*, per ADR-001's data-classification-in-manifest principle.

---

## D. Open questions for the Mission Owner

These are questions I cannot resolve from the baseline. I will proceed with the stated default and flag the dependency; none of them block producing the architecture.

**Q-1 (default: monorepo, model A).** ADR-001 chose "monorepo now, migratable to package later." Does the Mission Platform inherit that choice, or is the review an opportunity to move to multi-repo (platform as a versioned package, payloads as separate repos) from day one? *Default: inherit monorepo model A — lower friction, reversible.*

**Q-2 (default: yes).** Should the vertical slice prove the contract by *wrapping the existing camera logic* behind a `PayloadDriver` (additive, ADR-001 §7), or by *re-implementing* a minimal timelapse payload from scratch in the new structure? *Default: wrap-first to prove the contract, then re-implement — additive per project principle.*

**Q-3 (default: keep Python).** Is there appetite to reconsider the edge runtime? The edge already ships a C++ NPU component (`edge/npu_viplite/`) for VIPLite AI. If future payloads are AI-heavy, a polyglot edge (Python orchestration + native compute) may serve better than pure Python. *Default: keep Python as the contract/orchestration layer; treat NPU code as a payload-owned native dependency.*

**Q-4 (default: fail-closed, separate process).** ADR-001 amendment 1 says payloads run in a "separate OS-sandboxed process or equivalent enforcement boundary." On the Orange Pi (Armbian, systemd), the realistic enforcement options are: (a) separate systemd services with per-service users + seccomp/AppArmor, (b) containerd/microVMs (heavy), (c) systemd-nspawn. Which isolation primitive should the platform standardize on? *Default: separate systemd services + dedicated users + seccomp — lowest overhead, matches the existing systemd-based edge, sufficient for the threat model.*

**Q-5 (default: dual SemVer contracts as in ADR-001 §4).** Should the control-plane and data-plane contracts (amendment 2) be two independent versioned interfaces, or one interface with versioned sub-channels? *Default: two independent SemVer contracts — matches the accepted amendment and keeps change cost honest.*

**Q-6 (default: platform owns SIEM/CMDB/ops AI; payload owns domain AI).** Confirming the AI domain split (ADR-001 AI-domain amendment): platform-owned AI = SIEM/CMDB/drift/ops; payload-owned AI = camera analysis, tagging, edge QA, site-look. Shared *infrastructure* (Ollama, Gemini adapters) but domain-owned *purpose, prompts, data classification, retention, result ownership*. *Default: adopt as stated.*

**Q-7 (default: defer).** Does the Mission Platform need to support **customer-owned/third-party signed payloads** at launch, or is first-party-only acceptable until a second mission package exists (ADR-0007's review trigger)? *Default: first-party-only at launch; design the trust model so multi-vendor is additive later.*

---

## E. Bias acknowledgement

Per my opening transparency note: I authored four of the six REVIEW-001 governance documents in the immediately preceding BUILD-016 turn, including the submission checklist and meta-review criteria. The risk is that I "teach to the test." My mitigation: every architectural decision in this workspace is derived from the **TimeLapse Pro evidence and the mission**, with the Why/Because/For-whom trace recorded, so that bias toward the rubric is visible and correctable. I have not inspected, and will not inspect, any other reviewer's branch.
