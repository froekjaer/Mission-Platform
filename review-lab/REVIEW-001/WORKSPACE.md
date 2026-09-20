# REVIEW-001 Workspace — Gemini

- **Reviewer:** Gemini
- **Repository:** `froekjaer/Mission-Platform`
- **Branch:** `review/review-001-gemini`
- **Source baseline:** `froekjaer/timelapse-pro@eed9e3c8c67369e1924c25a11908616220c3c753`

## Writable boundary

> This workspace is the ONLY writable location assigned to this reviewer.
> The reviewer SHALL NOT create or modify files outside the assigned workspace
> (this branch, inside `review-lab/REVIEW-001/`).

All REVIEW-001 work by this reviewer SHALL be written to this branch.

The source repository `froekjaer/timelapse-pro` is the **Immutable Reference
Implementation**. It SHALL be treated as read-only. No commit, push, branch,
pull request, issue, file modification, deletion, or reorganisation is
permitted there during REVIEW-001.

## Start here

1. Read the canonical invitation in
   `froekjaer/mission-framework/pilot-reviews/REVIEW-001/INVITATION.md`.
2. Read [`README.md`](README.md), [`BASELINE.md`](BASELINE.md) and
   [`SUBMISSION-CHECKLIST.md`](SUBMISSION-CHECKLIST.md) in this directory.
3. Inspect the complete TimeLapse Pro baseline, beginning with its
   authoritative onboarding document.
4. Record initial assumptions and questions before designing.
5. Work independently and do not inspect other reviewer branches.

## Required structure (BUILD-016)

This workspace uses the BUILD-016 structure, pre-seeded as subdirectories
alongside this file:

```text
review-lab/REVIEW-001/
  WORKSPACE.md        (this file)
  docs/
  adr/
  platform/
  payloads/
  implementation/
  migration/
  tests/
  evidence/
```

Each subdirectory is intentional. Place deliverables in the matching
subdirectory. Empty subdirectories are kept with `.gitkeep` so the structure
is preserved until content arrives. An alternative structure is allowed only
with a documented ADR and a full mapping to the required outputs.

## Prohibited directories

To keep reviewer workspaces isolated, this reviewer SHALL NOT create any of
the following outside this workspace:

- `shared/`
- `common/`
- `core/`
- root-level `platform/`

## Shared components

If common functionality is discovered that may apply across reviewers, it
SHALL be documented in this workspace (purpose, interface, ownership,
rationale) but SHALL NOT be implemented during the independent phase.

Selection of shared components belongs exclusively to the Meta Review.

## Independence

This reviewer SHALL work independently and SHALL NOT:

- inspect another reviewer's solution before the independent phase closes;
- reuse another reviewer's code;
- merge another reviewer's implementation;
- attempt to converge on another reviewer's design.

External sources, tools, and collaborators SHALL be disclosed.

## Deliverables

Each reviewer SHALL produce, inside this workspace:

- Business architecture
- Conceptual architecture
- Logical architecture
- Physical architecture
- Component model
- ADRs
- Migration strategy
- Operational model
- Implementation
- Tests
- Evidence
- Risk register
- Roadmap

Every material architectural decision SHALL answer **Why?**, **Because?**,
and **For whom?** with a traceable record. See the reviewer guide at
`froekjaer/mission-framework/pilot-reviews/REVIEW-001/REVIEWER-GUIDE.md`.

## Submission status

Status: `NOT STARTED`
Frozen commit: `TBD`

Update this section as work progresses. Submission is complete only when the
framework gate at
`froekjaer/mission-framework/pilot-reviews/REVIEW-001/SUBMISSION-CHECKLIST.md`
is satisfied and a frozen commit SHA is recorded above.

## Authority

Peter Frøkjær is Mission Owner and retains final authority over whether a
proposal serves the mission. The Mission Owner does not prescribe the
technical solution.
