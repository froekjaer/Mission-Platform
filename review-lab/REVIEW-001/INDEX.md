# REVIEW-001 — Frozen Archive Index

Purely navigational. No analysis, no comparison. Each directory below contains the complete, unmodified content of the named reviewer's branch (all files added or changed relative to `main`), copied byte-identically from the recorded commit. Original branches remain the authoritative source; byte-identity was verified at archive time (sha256 per file).

| Reviewer | Branch | Commit (frozen tip) | Freeze timestamp | Working language | Entry document | Evidence location | Notes |
|---|---|---|---|---|---|---|---|
| ChatGPT | `review/review-001-chatgpt` | `59ca47994ee6030f0d61f77779eb40c1ff65dceb` | 2026-07-25T21:40:27+02:00 | English | `chatgpt/docs/00-INITIAL-ASSESSMENT.md` | — (no evidence directory content) | Workspace scaffold plus one initial-assessment document at freeze time |
| Codex | `review/review-001-codex` | `b6549c49d8ea0a0ec67c7c42f2b859567a6fe64d` | 2026-07-25T14:52:56+02:00 | — | `codex/WORKSPACE.md` | — | Workspace scaffold only; no submission documents present at freeze time |
| Z.ai | `review/review-001-zai` | `3e99418ac6b5690b92ff3fc1a195b8d18e04fcc2` | 2026-07-25T20:23:36+02:00 | English | `z-ai/docs/EXECUTIVE_SUMMARY.md` | `z-ai/evidence/` | Includes executable implementation and tests |
| Kimi | `review/review-001-kimi` | `e96803a60f8f440af2e8f080f53a7bd55d32c96b` | 2026-07-29T06:43:25+02:00 | Mixed Danish/English | `kimi/00-EXECUTIVE-SUMMARY.md` | `kimi/evidence/` | Source branch already nested content under `kimi/`; that prefix is preserved once here |
| Gemini | `review/review-001-gemini` | `f7df11db782e5a64e6f904f4fe6e7525a99e4e8c` | 2026-07-31T02:12:28+02:00 | English | `gemini/GEMINI-SUBMISSION.md` | embedded in entry document | Submission delivered as a single consolidated document |
| Claude | `review/review-001-claude` | `c75b812368b689a3d52247bfec295bf887dd449e` | 2026-07-31T02:21:48+02:00 | English | `claude/docs/00-EXECUTIVE-SUMMARY.md` | `claude/evidence/` | Includes executable implementation and tests |

Shared lab documents (`README.md`, `BASELINE.md`, `SUBMISSION-CHECKLIST.md` template) at this directory's root come from `main` and were not authored by any single reviewer. Reviewer-modified copies of shared files (e.g. `WORKSPACE.md`, completed checklists) live inside each reviewer directory.

Machine-readable version of this index: `MANIFEST.yaml`. Freeze declaration: `REVIEW-001-FREEZE.md`.
