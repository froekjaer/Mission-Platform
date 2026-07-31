# ADR-CL-003: Decompose the headend by plane before generalising the edge

**Status:** Proposed · **Date:** 2026-07-31

## Context

`headend/main.py` is 18,541 lines with 234 direct routes; the ratchet only freezes it. Source planning (P2-01) treats decomposition as refactoring debt; source ADR-001 focuses its architecture on the edge. Yet the headend carries the exposed attack surface, the auth failure class, and every future payload's server side. The edge, by contrast, is already half-modular (F-06).

## Decision

Sequence the transformation **headend-first**, decomposing by the four-quadrant model (platform-control, platform-data, payload-domain, experience) into logically separate services with these hard rules: composition-only `main.py` (ratchet re-targeted to shrink to < 300 lines), authenticated-router-by-construction (auth failure class becomes impossible, not just detected), and payload-domain routes (tagging, video, site look) mounted as a distinct service consuming platform interfaces.

Initially one process, four packages — process separation is a later, cheap step because the boundaries are already package boundaries.

**Why?** Biggest risk first: the headend is where security regressions recur and where go-live blockers live. **Because?** O-02/S-04; strangler economics — headend routes can move incrementally with the existing test suite as a net, while edge re-architecture risks the running capture fleet for less gain. **For whom?** Customers and operator (exposed surface hardened first); future payloads (their server side gets a defined home, which source ADR-001 never gave it).

## Alternatives

Edge-first (source plan's implicit order — rejected: optimises the already-better half); big-bang service split (rejected: no safety net, solo operator); leave headend to "P2-01 someday" (rejected: that is how it reached 18.5k lines).

## Consequences

Positive: every extraction directly reduces the exposed monolith; migration stages align with go-live blockers (ADR-CL-006). Negative: edge developers (future payloads) wait longer for the final edge supervisor; mitigated by the vertical slice proving the edge contracts in simulation now.

## Validation path

Ratchet trend (lines/routes in `main.py`) is the progress metric, reviewable per release; route-auth sweep stays green throughout; rollback = any extraction is a git-revertible additive move (old route delegates to new service until cutover verified).
