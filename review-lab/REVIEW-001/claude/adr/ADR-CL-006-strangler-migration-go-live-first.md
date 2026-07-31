# ADR-CL-006: Strangler migration, go-live-first sequencing

**Status:** Proposed · **Date:** 2026-07-31

## Context

Baseline S-01: platform work competes with production readiness; the source's own no-go blockers (backup evidence, GDPR, exposure design, MFA cleanup) are unresolved. A migration plan that delays go-live to build platform purity would damage the mission it serves.

## Decision

Migration is a **strangler pattern over the running system**, sequenced so that **every early stage closes go-live blockers while creating platform structure** — platform work and production-readiness work are the same commits. Five stages, each additive, gated and reversible (full plan: `migration/migration-strategy.md`). No stage renames existing data contracts; no stage deletes source evidence (quarantine only); the running lab fleet stays on TimeLapse Pro `main` until stage cutovers are individually verified.

**Why?** The platform must earn its keep immediately. **Because?** Source amendment 6 requires gate-driven additive migration; this ADR gives it teeth by making blocker-closure the gate currency. **For whom?** Mission Owner (go-live sooner, not later), customers (no service risk), Meta Review (mergeable increments instead of a parallel universe).

## Alternatives

Greenfield rebuild in Mission-Platform repo with later data migration (rejected: two systems to run alone, evidence debt duplicated); freeze features until platform done (rejected: business starves); per-module opportunistic refactoring without stage gates (rejected: that is the status quo that produced the monolith).

## Consequences

Positive: value at every stage; abort-safe at every gate. Negative: strangler discipline (old+new coexisting) is cognitively heavier per step than a rewrite; mitigated by small stages and the ratchet metrics.

## Validation path

Each stage's exit gate lists machine-checkable criteria (migration-strategy.md); the roadmap's "next safe step" is always the smallest reversible commit of the current stage.
