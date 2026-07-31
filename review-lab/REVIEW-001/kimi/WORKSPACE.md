# REVIEW-001 — Kimi Workspace

## Reviewer

Kimi

## Branch

`review/review-001-kimi`

## Purpose

This workspace is the only writable area assigned to Kimi for REVIEW-001.

Kimi SHALL perform the review independently and SHALL NOT inspect, modify, compare against, or derive from any other reviewer's branch or workspace.

## Repository roles

- `froekjaer/mission-framework` — Governance Repository. Read the REVIEW-001 governance material before beginning technical work.
- `froekjaer/timelapse-pro` — Immutable Reference Implementation. Read-only evidence source. No branches, commits, pull requests, issues, or modifications.
- `froekjaer/Mission-Platform` — Implementation Repository. All Kimi deliverables belong on this branch and inside this workspace.

## Mandatory starting point

Read the following before beginning the review:

```text
froekjaer/mission-framework
pilot-reviews/REVIEW-001/
    README.md
    INVITATION.md
    REVIEW-PROCESS.md
    REVIEWER-GUIDE.md
    SUBMISSION-CHECKLIST.md
    META-REVIEW.md
```

Then inspect `froekjaer/timelapse-pro` as read-only evidence.

## Mission

Do not reproduce TimeLapse Pro.

Design the best possible Mission Platform using TimeLapse Pro as evidence, while preserving a clear separation between platform capabilities and payload-specific behavior.

Independent thinking is a success criterion. Kimi is explicitly encouraged to:

- challenge assumptions
- simplify where justified
- introduce new ideas
- disagree with existing architecture where evidence supports doing so
- document reasoning using Why / Because / For whom

## Writable boundary

Kimi SHALL write only inside:

```text
review-lab/REVIEW-001/kimi/
```

Kimi SHALL NOT create or modify shared platform, common, core, or cross-reviewer material outside this workspace.

If Kimi identifies functionality that should become shared or common, document it as a proposal for Meta Review rather than implementing it outside the workspace.

## Expected structure

```text
review-lab/REVIEW-001/kimi/
    WORKSPACE.md
    docs/
    adr/
    platform/
    payloads/
    implementation/
    migration/
    tests/
    evidence/
```

Additional subdirectories are allowed when justified, but all work must remain under the assigned workspace.

## Submission discipline

Before freezing the submission, Kimi SHALL:

- complete all required REVIEW-001 deliverables
- document assumptions, evidence, risks, limitations, and unresolved questions
- declare any material bias or prior exposure
- verify the immutable reference repository remains unchanged
- verify no other reviewer branch or workspace was inspected or modified
- record test and evidence status honestly
- create a final freeze commit
- stop implementation after freezing pending Meta Review

## Freeze declaration

The final submission report should include:

- frozen commit SHA
- freeze date
- deliverable count
- verification results
- test/evidence results
- architectural thesis
- load-bearing decisions
- bias disclosure
- honest limitations
- one next safe step

Welcome to REVIEW-001, Kimi.

You are not being asked to agree with the existing work or with any other reviewer. You are being asked to make the strongest independent, evidence-based contribution you can.
