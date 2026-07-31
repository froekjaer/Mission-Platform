# ADR-CL-001: ADR convention and review method

**Status:** Accepted (reviewer scope) · **Date:** 2026-07-31

## Context

The source repo has two ADRs with incompatible numbering and templates (ADR-001, ADR-0007) and the ADR process rule lives inside a risk addendum (K6). This workspace needs one convention before producing decisions. The review needs a declared method (see `docs/INTAKE.md` §1).

## Decision

Namespace `ADR-CL-NNN`, contiguous numbering, single template (Status/Context/Decision/Why–Because–For whom/Alternatives/Consequences/Validation), register in `adr/README.md`. Method: SABSA layer spine + C4 notation + hexagonal contract thinking; every material decision answers the three mandatory questions.

**Why?** Traceability and comparability in the Meta Review. **Because?** Source O-06 shows numbering drift already happening at n=2. **For whom?** Meta Review and future maintainers.

## Alternatives

Continue source numbering (rejected: collides across parallel reviewer branches); MADR format (fine, but the project's own three-question rule is the differentiator worth keeping).

## Consequences

Recommendation to Meta Review: whichever branch wins, adopt one ADR convention on `main` and renumber the two source ADRs into it (additively, with redirects).
