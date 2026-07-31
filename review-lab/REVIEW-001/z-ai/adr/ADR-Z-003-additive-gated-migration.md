---
id: ADR-Z-003
title: Migration is additive, wrap-first, and ratchet-gated
status: Proposed
date: 2026-07-25
deciders: Z.ai (reviewer proposal; Mission Owner decides)
supersedes: none
relates_to: timelapse-pro ADR-001 §7 (K1-K6 governance) + amendment 6 (additive migration); P2-01 refactor plan
---

# ADR-Z-003 — Migration is additive, wrap-first, and ratchet-gated

## Context

The Mission Platform is derived from a working production system (TimeLapse Pro) that must stay in production throughout. ADR-001 amendment 6 mandates "additive, gate-steered migration so the generic platform vision does not delay TimeLapse Pro production-readiness." The risk is a big-bang refactor that breaks paying customers. The `headend/main.py` monolith (234 routes, repeated route-auth failures) is the principal debt, and P2-01 (`P2-01_Refaktoreringsplan_main_py.md`) already proposes a refactor plan that needs a *target*.

## Decision

**Migration follows four ordered principles:**

1. **Contract-first, then wrap, then extract.** Define the contract (ADR-Z-001), wrap existing timelapse capture logic behind it *in place*, prove the contract fits reality, *then* extract modules toward the logical structure. No code moves until the contract is proven against today's behaviour.

2. **Additive naming, no broad renames.** New domain-neutral names (`node`, `asset`) are additive; existing `camera`/`capture` are not renamed broadly (ADR-001 §5). No schema break before live verification (project principle).

3. **Ratchet-only governance.** Inherit and extend TimeLapse Pro's existing K1–K6 controls:
   - K1 route-auth-sweep (`test_route_auth_coverage.py`) — every extracted router must pass.
   - K2 no-new-endpoints-in-main.py — extraction target is enforced.
   - K3 ratchet gates (`test_architecture_ratchet.py` + `architecture_baseline.json`) — main.py line/route ceiling may only ever *decrease*; raising requires a documented exception.
   - K4 step-up on sensitive actions.
   - K5 commit-before-deploy.
   - K6 ADR process for material changes (this very ADR).
   - **K7 (new):** every payload must pass the contract test suite before load (ADR-Z-001).

4. **Reversibility until validated.** Each migration step is independently reversible (quarantine, not hard-delete — project principle "aldrig hard-delete"). A failed extraction is rolled back, not patched forward.

## Why (business attribute)

Manageability, Integrity, Continuity. Paying customers must not lose service; the integrity guarantee must not regress; the system must remain manageable throughout.

## Because (evidence/reasoning)

- The project's own principle is "additive + flag-guarded; no schema break before live verification; never hard-delete." This ADR operationalises that principle for the platform migration.
- K1–K6 already exist in the TimeLapse Pro codebase and are cited in `00_START_HER.md` as governance gates — inheriting them is zero-cost and proven.
- The monolith's repeated route-auth failures prove that *without a ratchet*, debt regenerates; the ratchet is the mechanism that makes the refactor stick.
- ADR-001 §7 explicitly makes debt-paydown and modularisation "the same work" — this ADR sequences that work safely.

## For whom

Paying timelapse customers (continuity of service); the operator/on-call engineer (no surprise outages); the Mission Owner (production-readiness not delayed); future maintainers (a ratcheted codebase is a gift).

## Alternatives considered

- **Big-bang rewrite.** Rejected: violates amendment 6, endangers paying customers, and discards the working integrity chain. ADR-001 rejected the analogous "full microservices now."
- **Strangler-fig without a contract.** Rejected: without a target contract, extraction is ad hoc and the debt regenerates (the current situation).
- **Freeze-and-fork.** Rejected: TimeLapse Pro must keep shipping; a fork diverges from live customer evidence.

## Consequences

- **Positive:** production continuity; the refactor sticks (ratchet); debt paydown and platform-building become one budget; every step is auditable.
- **Negative:** slower apparent progress than a rewrite; requires discipline to not raise ratchet ceilings; the contract must be right early (ADR-Z-001 risk).
- **Neutral:** migration sequence detail lives in the Migration Strategy document, not here.

## Sequencing summary (detail in Migration Strategy)

```
Step 0  contract spike: PayloadDriver + manifest schema + timelapse wrap + tests
Step 1  extract platform/hal, platform/config, platform/identity (already half-modular on edge)
Step 2  extract platform/supervisor + isolation (ADR-Z-002) — load timelapse as first payload
Step 3  decompose headend main.py routers behind K1/K2/K3 (ratchet only tightens)
Step 4  extract platform/tenants, platform/audit, platform/access (JIT broker)
Step 5  second (stub) payload to prove Extensibility (the ADR-0007 review trigger, on purpose)
```

## Validation path (reversible)

Step 0 is the proof: if the contract cannot wrap today's capture logic cleanly, the contract (not the capture logic) is revised. Every later step is gated by tests + ratchet + K1–K7.
