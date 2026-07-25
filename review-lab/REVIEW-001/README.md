# REVIEW-001 — Mission Platform Transformation Lab

This directory defines the shared, controlled environment for independent transformations of TimeLapse Pro into Mission Platform.

## Canonical invitation

The binding mission and reviewer instructions are maintained in:

- `froekjaer/mission-framework/pilot-reviews/REVIEW-001/INVITATION.md`

## Frozen source baseline

- Source repository: `froekjaer/timelapse-pro`
- Baseline commit: `eed9e3c8c67369e1924c25a11908616220c3c753`
- Baseline purpose: common evidence and migration source for all reviewers

The source baseline must not move during the independent phase. A later source update requires an explicit REVIEW-001 baseline decision and a documented impact assessment.

## Reviewer workspaces

Each independent reviewer works on a dedicated branch created from the same Mission Platform baseline:

- `review/review-001-chatgpt`
- `review/review-001-claude`
- `review/review-001-gemini`
- `review/review-001-codex`
- `review/review-001-zai`
- `review/review-001-human`

The reviewer branches are experimental workspaces. They are not release branches and must not be merged directly into `main`.

## Shared repository structure

Reviewers should preserve or create the following logical structure in their branch:

```text
review-lab/REVIEW-001/
  README.md
  BASELINE.md
  SUBMISSION-CHECKLIST.md

docs/
  mission/
  architecture/
  adr/
  evidence/
  migration/
  operations/

platform-core/
payload-sdk/
payloads/
  timelapse/
deployments/
  timelapse-reference/
tests/
tooling/
```

The exact implementation structure may differ when justified by an ADR. The required architectural separation and deliverables remain binding.

## Isolation rule

During the independent phase, reviewers must not inspect another reviewer branch. The Mission Owner may answer clarification questions but should avoid revealing another solution or steering all reviewers toward one design.

## Submission gate

A reviewer submission is complete only when:

1. the required outputs in the invitation exist;
2. material decisions have ADRs;
3. the source baseline and migrated elements are traceable;
4. executable claims have test or runtime evidence;
5. risks, assumptions and unresolved questions are explicit;
6. the submission checklist is complete;
7. a final commit SHA and handover are recorded.

## Meta-review

After all submissions are frozen, Mission Framework performs a blind comparison. The output is not a popularity vote and no complete branch wins by default. The meta-review selects supported architectural elements, records dissent and creates a separately governed integration plan for `main`.
