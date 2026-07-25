# REVIEW-001 Frozen Baseline

## Source

- Repository: `froekjaer/timelapse-pro`
- Branch at selection: `main`
- Frozen commit: `eed9e3c8c67369e1924c25a11908616220c3c753`
- Commit subject: `Extract Edge provisioning security services`

## Destination baseline

- Repository: `froekjaer/Mission-Platform`
- Shared lab commit: this file and the REVIEW-001 lab documents on `main`
- Reviewer branches must be created only after the shared lab documents are present.

## Baseline policy

The TimeLapse Pro commit above is the common reference for all independent reviewers. Reviewers may copy, extract, adapt or replace elements from it, but every migrated or rejected component must be traceable to the source or to a documented new decision.

No reviewer may silently substitute a later TimeLapse Pro commit. When a critical correction is discovered after the freeze, record it as a baseline exception with:

- affected source files and commits;
- reason for inclusion;
- impact on all reviewer workspaces;
- whether all reviewers received the same correction;
- Mission Owner approval.

## Existing authority hierarchy

For claims about the source system, prefer in this order:

1. verified runtime evidence;
2. current code and automated tests;
3. accepted ADRs;
4. authoritative current documentation;
5. historical documentation and discussion.

Conflicts must be recorded rather than silently reconciled.

## Initial architectural fact

TimeLapse Pro already contains an accepted Platform/Payload direction. Reviewers must examine this decision as evidence. They may retain, refine or challenge it through a new ADR, but may not ignore it.

## Preservation

`froekjaer/timelapse-pro` remains the operational and historical source system during REVIEW-001. Mission Platform work does not replace it until a separately approved migration and acceptance decision is completed.
