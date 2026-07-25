# Handover — Z.ai REVIEW-001 Submission

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Frozen submission commit:** see `git log -1 review/review-001-zai` — the commit that adds this handover is the freeze commit.
**Submission date:** 2026-07-25

---

## 1. What this submission is, in 30 seconds

TimeLapse Pro's *architecture* (ADR-001 platform/payload split, ADR-0007 product→platform) is excellent and already accepted. Its *code* is a 234-route monolith that hasn't caught up. This submission closes that **intent-vs-enforcement gap**: it makes the PayloadDriver contract a tested, versioned, fail-closed boundary; runs payloads in isolated systemd+seccomp tenants; and migrates additively behind ratchet gates so the paying timelapse service never breaks. A 17-test vertical slice proves the contract, the fail-closed enforcement, and that a second payload loads with zero platform changes.

## 2. The three things to read first

1. `docs/EXECUTIVE_SUMMARY.md` — the problem, the three load-bearing decisions, what is/isn't proved.
2. `docs/BUSINESS_ARCHITECTURE.md` — the mission, stakeholders, and the 13 business attributes every lower layer traces to.
3. `adr/ADR-Z-001` + `ADR-Z-002` + `ADR-Z-003` — the three material decisions, each challengeable and reversible.

## 3. The three things I most want a human reviewer to check

1. **ADR-Z-002's isolation primitive** (systemd+seccomp). I reasoned this from documentation, not from bench experience on the Orange Pi. An OT engineer's validation is the single highest-value review action. This is open question **Q-4**.
2. **The migration sequencing** (Roadmap Phase 0→5). Am I being realistic about ratchet discipline, or optimistic? Someone who has operated TimeLapse Pro in anger should pressure-test Steps 2–3.
3. **The bias risk.** I wrote the REVIEW-001 governance immediately before this submission. The meta-review should discount where my choices conveniently match rubric items. I traced every decision to TimeLapse Pro evidence to make bias visible, but I cannot fully self-audit it.

## 4. The next safe step (one sentence)

**Port the vertical slice's `SyntheticCapture` to a real `Gphoto2Capture` wrapping the existing Nikon Z30 driver, and run the capability-enforcement test on the active edge node `TL-C87FF9587CA0`.** If the contract holds against real hardware, every later migration step is unlocked; if not, the contract is revised before any production code moves.

## 5. What is explicitly NOT done (do not mistake for gaps in thinking)

- The 11 🔴 production blockers (intern CA/mTLS, disk encryption, backup/restore evidence, GDPR DPIA, redaction, etc.) — catalogued in Risk Register §B, given a clean architectural home, but not implemented. They are productionisation work (Sprints H–N), not architecture work.
- Multi-headend federation and multi-vendor payload trust — deferred by ADR-001, consistent with ADR-0007's review trigger.
- A real second vertical (waterworks/energy/maritime) — a stub proves Extensibility; a real payload comes when a vertical is on the horizon.

## 6. Open decisions for the Mission Owner (Q-1 to Q-7)

Recorded in `docs/ASSUMPTIONS_AND_QUESTIONS.md`. The two that most affect the architecture:

- **Q-4** (isolation primitive: systemd+seccomp vs. containers) — default systemd+seccomp; reversible.
- **Q-7** (third-party payloads at launch?) — default first-party-only; if "yes" earlier than expected, R-Z-02 severity escalates and ADR-Z-002 should be revisited.

## 7. Independence statement (for the meta-review)

I have not inspected and will not inspect the `chatgpt`, `claude`, `gemini`, `codex`, or `human` branches. Any convergence between my submission and another reviewer's is independent convergence on the same evidence (ADR-001 already records that Claude and Codex independently reached the same platform/payload conclusion — convergence on strong evidence is expected and is information, not collusion).

## 8. Freeze

Implementation stopped at this commit. No further work on this branch until the meta-review concludes, per the REVIEW-001 process.
