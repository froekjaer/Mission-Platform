# REVIEW-001 — Human workspace

This is the independent reviewer workspace for **human** in REVIEW-001.

## Identification

- **Repository:** `froekjaer/Mission-Platform`
- **Branch:** `review/review-001-human`
- **Workspace:** `review-lab/REVIEW-001/human/`

## Writable boundary

> This workspace is the ONLY writable location assigned to this reviewer.
> The reviewer SHALL NOT create or modify files outside the assigned workspace.

All REVIEW-001 work by this reviewer SHALL be written to this workspace on the branch above.

## Required structure

This workspace is pre-seeded with the BUILD-016 structure:

```text
human/
  README.md
  docs/
  adr/
  platform/
  payloads/
  implementation/
  migration/
  tests/
  evidence/
```

Each subdirectory is intentional. Place deliverables in the matching subdirectory. Empty subdirectories are kept with `.gitkeep` so the structure is preserved until content arrives.

## Prohibited directories

To keep reviewer workspaces isolated, this reviewer SHALL NOT create any of the following outside this workspace:

- `shared/`
- `common/`
- `core/`
- root-level `platform/`

## Shared components

If common functionality is discovered that may apply across reviewers, it SHALL be documented in this workspace (purpose, interface, ownership, rationale) but SHALL NOT be implemented during the independent phase.

Selection of shared components belongs exclusively to the Meta Review.

## Independence

This reviewer SHALL work independently and SHALL NOT:

- inspect another reviewer's solution before the independent phase closes;
- reuse another reviewer's code;
- merge another reviewer's implementation.

## Reference documents

- Invitation (binding): `froekjaer/mission-framework/pilot-reviews/REVIEW-001/INVITATION.md`
- Review process: `froekjaer/mission-framework/pilot-reviews/REVIEW-001/REVIEW-PROCESS.md`
- Reviewer guide: `froekjaer/mission-framework/pilot-reviews/REVIEW-001/REVIEWER-GUIDE.md`
- Framework submission gate: `froekjaer/mission-framework/pilot-reviews/REVIEW-001/SUBMISSION-CHECKLIST.md`
- Meta-review: `froekjaer/mission-framework/pilot-reviews/REVIEW-001/META-REVIEW.md`
- Shared lab baseline: [`../README.md`](../README.md)
- Frozen source baseline: [`../BASELINE.md`](../BASELINE.md) — `eed9e3c8c67369e1924c25a11908616220c3c753`
- Reviewer-fillable submission checklist: [`../SUBMISSION-CHECKLIST.md`](../SUBMISSION-CHECKLIST.md)

## Source repository — read only

`froekjaer/timelapse-pro` is the Immutable Reference Implementation for REVIEW-001. It SHALL be treated as read-only. No write of any kind is permitted there.
