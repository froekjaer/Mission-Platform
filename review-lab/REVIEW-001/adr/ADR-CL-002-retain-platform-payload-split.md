# ADR-CL-002: Retain and refine the Platform/Payload split

**Status:** Proposed · **Date:** 2026-07-31 · **Examines:** source ADR-001 (Accepted 2026-07-16), source ADR-0007 (Proposed)

## Context

BASELINE.md requires each reviewer to examine the accepted Platform/Payload direction as evidence and retain, refine or challenge it via a new ADR. Independent analysis of the baseline (evidence/baseline-evaluation.md) confirms the forcing functions are real: monolith growth with a thrice-repeated auth failure class (F-03, F-05), a domain minority of code that is actually timelapse-specific, and a documented OT ambition.

## Decision

**Retain** the Platform/Payload split, the `PayloadDriver` + capability manifest concept, monorepo model A, SemVer'd contracts, additive naming, fail-closed capability validation, control/data-plane separation, AI domain split and JIT conduit model — all as in source ADR-001 with its amendments.

**Refine** in four places:

1. **Control/data-plane separation is promoted from amendment to first-class structural cut** applied to the *headend as much as the edge* (see ADR-CL-003). Source ADR-001 is edge-centric; the baseline's largest liability is the headend (O-02).
2. **The data contract is narrowed to three channel kinds** (blob, timeseries, event) with mandatory classification and retention class — small enough to implement now, sufficient for timelapse and the named OT test cases (analysis: waterworks = timeseries + event; maritime/SDR = all three kinds; nothing named needs more in v1).
3. **The anti-coupling invariant is made machine-enforced** (CI import-boundary test + a permanently maintained simulated second payload) rather than review-enforced. Evidence: vertical slice `tests/`.
4. **Right-sizing rule:** platform features are admitted only against a named payload need or a named risk — guarding the one-operator economy (O-07) against platform-for-its-own-sake growth, which is the characteristic failure mode of "product → platform" evolutions.

**Why?** The split is the only structure that makes the OT ambition testable without forking the codebase. **Because?** Independent examination reproduced the source decision's forcing functions from the raw evidence; the refinements close the gaps the source decision left (headend, enforcement, scope discipline). **For whom?** Operator (bounded effort), customers (contained failures), future OT missions (safety boundary exists from day 1).

## Alternatives considered

- **Challenge: stay a product, defer platformisation until a second paying vertical exists.** Seriously considered — it is the cheapest path for the next 6 months. Rejected because the *same work* (decomposing the monolith, killing the auth failure class, closing go-live blockers) is needed for the product alone; doing it against neutral contracts costs little extra and is the only way the OT option retains value. The refinement 4 rule is the guard against over-rotation.
- **Challenge: microservices/event-driven rewrite.** Rejected: violates one-operator proportionality; the baseline shows no scale pressure that demands it.

## Consequences

Positive: continuity with accepted direction, so Meta Review disagreement surface is narrowed to the refinements. Negative: contract discipline (SemVer, compatibility matrix) is real ongoing overhead; accepted as the price of the OT option. 

## Validation path

Vertical slice proves contracts fit the real timelapse capture flow (implementation/); SPIKE-01 (ADR-CL-005) proves isolation affordability; second-payload smoke test proves neutrality continuously. Reversal: if refinement 2's channel kinds prove insufficient for a real payload, that is a contract major bump with documented migration — not a silent widening.
