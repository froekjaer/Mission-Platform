# Executive Summary — Z.ai REVIEW-001 Submission

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Frozen submission commit:** *(recorded at submission freeze)*
**Date:** 2026-07-25

---

## The problem, in one paragraph

TimeLapse Pro is a working Danish timelapse SaaS whose **architecture has outgrown its code**. The documentation already commits to a platform/payload split (ADR-001, accepted 2026-07-16) and a product-to-platform evolution (ADR-0007, proposed 2026-07-22). But the headend is a single **~18,000-line `main.py` with 234 routes**, the same route-auth failure class has recurred three times (SEC-001, R15, R22), and the platform/payload boundary exists as *intent and partial edge modularity*, not as an enforced contract. The risk is not that the architecture is wrong — it is unusually well-reasoned — but that the gap between *accepted architecture* and *enforced architecture* will widen until a second payload becomes impossible to add safely.

## What I propose

A **Mission Platform** that makes TimeLapse Pro's accepted architecture *load-bearing*: the platform/payload contract becomes a versioned, tested, fail-closed boundary; the monolith is decomposed along the lines ADR-001 already drew; and timelapse becomes the first payload that proves the contract works. The design preserves every SABSA business attribute the system already delivers (lens-to-archive SHA-256 integrity, store-and-forward autonomy, tenant isolation, time-synchronised capture) and adds the ones ADR-001 promises but the code does not yet enforce (real process isolation, separate control/data planes, fail-closed capability validation, JIT conduits).

## The three load-bearing decisions

1. **The contract is the product, not the timelapse code.** The `PayloadDriver` + capability-manifest contract (ADR-001 §2) is promoted from "normative sketch" to a first-class, SemVer-versioned, test-covered artifact. Everything else — platform extraction, payload packaging, migration sequencing — flows from making the contract real. *(ADR-Z-001.)*

2. **Isolation is an enforcement boundary, declared in code.** Per ADR-001 amendment 1, payloads run as separate systemd services with dedicated users and seccomp profiles, not as in-process Python objects. The manifest *declares*; platform policy *enforces*. This is what makes the OT-vertical promise (waterworks, energy, maritime) credible for IEC 62443 zone/conduit and CRA secure-by-design. *(ADR-Z-002.)*

3. **Migration is additive and gated, never big-bang.** The existing camera logic is wrapped behind the contract first (proving the contract fits reality), then extracted into a payload package, then the monolith is decomposed behind ratchet gates that only ever tighten — directly inheriting the project's existing K1–K6 governance controls and `test_architecture_ratchet.py`. TimeLapse Pro stays in production throughout. *(Migration strategy + ADR-Z-003.)*

## What is proved

A **vertical slice**: a minimal platform core (identity, config hierarchy, capability manifest loader, PayloadDriver lifecycle) plus a timelapse payload that wraps real capture logic behind the contract, with contract tests and a capability-manifest enforcement test that demonstrates fail-closed behaviour on an undeclared capability. The slice is executable and reproducible; it is not a feature-complete reimplementation of 82 requirements.

## What is explicitly not done

- No reimplementation of the 11 🔴 hard blockers (intern CA/mTLS, disk encryption, backup/restore evidence, GDPR DPIA). These are catalogued in the migration plan and risk register with owners and sequencing; they belong to the productionisation track, not the architecture proof.
- No multi-headend federation, no multi-vendor trust ecosystem (deferred by ADR-001, consistent with ADR-0007's review trigger).
- No assumption that this submission is "the winner." Per the meta-review process, divergence is information.

## Headline recommendation for the Mission Owner

Adopt ADR-001's direction *as the platform spine*, but close the **intent-vs-enforcement gap** by making the contract and the isolation boundary test-enforced from the first commit. Treat the monolith decomposition as the *same work* as debt paydown (P2-01) — not a separate refactor — so the investment pays back even if no second payload ever ships.

## Confidence

- **High** that the direction is correct: it is already accepted in ADR-001 and independently converged on by Claude and Codex per the ADR record.
- **High** that the contract-and-isolation approach is the right *shape*; it is standard for OT/edge platforms and maps cleanly to IEC 62443 zones/conduits.
- **Medium** on isolation primitive choice (systemd+seccomp vs. alternatives) — this is Q-4, deferred to the Mission Owner.
- **Medium** on migration sequencing details, which depend on production-readiness priorities I have catalogued but not re-prioritised.

## Next safe step

Implement the contract spike (ADR-001 "opfølgning ved accept" step 3): define `contracts/PayloadDriver` + manifest schema, wrap the existing camera `tick()` behind it, and prove the contract tests pass against today's capture code — before any code is moved. This is reversible, additive, and unblocks everything else.
