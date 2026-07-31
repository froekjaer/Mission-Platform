---
id: ADR-Z-001
title: The PayloadDriver contract is the product
status: Proposed
date: 2026-07-25
deciders: Z.ai (reviewer proposal; Mission Owner decides)
supersedes: none
relates_to: timelapse-pro ADR-001 §2 (PayloadDriver + capability manifest)
---

# ADR-Z-001 — The PayloadDriver contract is the product

## Context

TimeLapse Pro ADR-001 (Accepted 2026-07-16) introduces a `PayloadDriver` + capability-manifest contract as the coupling between platform and payload, but describes it as a "normative sketch — details forfines in ADR-002." ADR-002 was never written. The result: the *most important artifact in the architecture* exists as prose, not as tested, versioned, enforced code. Meanwhile the monolith (`main.py`, 234 routes) keeps growing because there is no contract to extract *toward*.

## Decision

**Promote the contract to a first-class product artifact.** Specifically:

1. `contracts/` is a top-level package with its own SemVer, owned jointly but changed deliberately.
2. The control-plane contract (`PayloadDriver`) and data-plane contract are separate, versioned, and each has a **contract test suite** that any payload must pass to load.
3. The capability manifest is a **schema-validated artifact**; a payload whose manifest does not validate does not load, fail-closed.
4. CI enforces: platform and payload must agree on contract version; manifest schema changes are major bumps.

## Why (business attribute)

Extensibility and Proportionate compliance. The platform's entire reason for existing is to host payloads safely; if the contract is informal, extensibility is a slogan, not a property.

## Because (evidence/reasoning)

- ADR-001 already commits to the contract shape; this ADR makes it *load-bearing* rather than aspirational.
- The repeated route-auth failures (SEC-001, R15, R22) are symptoms of extraction-without-target; a real contract gives extraction a destination.
- Contract tests are the cheapest way to prove "a second payload can be added without touching platform internals" (Business Arch §4 Extensibility criterion).

## For whom

Future payload owners (waterworks, energy, maritime) who need a documented contract to build against; the Mission Owner whose open-source-OT vision requires a stable interface; reviewers/meta-review who need something testable to compare.

## Alternatives considered

- **Keep the contract as prose (status quo).** Rejected: it is exactly the intent-vs-enforcement gap this review exists to close.
- **Use an off-the-shelf plugin framework.** Rejected for now: introduces foreign abstractions and trust assumptions before the in-house contract has proven itself; the existing `edge/camera/drivers/registry.py` already shows a homegrown driver pattern that works.

## Consequences

- **Positive:** extraction gets a target; a second payload becomes provably cheap; the contract becomes reviewable and versionable.
- **Negative:** the contract is now the most expensive thing to change — SemVer discipline becomes mandatory, and a breaking change requires coordinated platform+payload work.
- **Neutral:** this ADR does not choose the contract's *content* in full; ADR-Z-002 and the implementation specify isolation, ADR-Z-003 specifies migration.

## Validation path (reversible)

Implement a minimal contract + one timelapse payload wrapping existing capture + contract tests. If the contract cannot express today's timelapse behaviour, revise the contract before extracting anything else. Fully reversible: no production code moves until the contract is proven.
