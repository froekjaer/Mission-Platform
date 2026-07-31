# Risk Register — Mission Platform Proposal (Claude)

- **Date:** 2026-07-31 · Owner column names who holds the risk if this proposal is adopted. L/C: Low/Med/High likelihood & consequence.

| ID | Risk | L | C | Owner | Treatment | Trigger to revisit |
|---|---|---|---|---|---|---|
| RR-01 | Platform work displaces production go-live (source S-01) | M | H | Mission Owner | ADR-CL-006: stages 0–2 ARE go-live work; roadmap forbids stage 4+ without business trigger | any stage slipping >1 cycle |
| RR-02 | Contract v1 mis-sized; first real OT payload needs breaking change (S-02) | M | M | Architecture (Claude proposal) | narrow v1 (3 channel kinds); waterworks simulator exercises the seam continuously; SemVer major path documented | second real payload committed |
| RR-03 | Isolation unaffordable/broken on Orange Pi (S-03) — **primary unvalidated claim of this submission** | M | H | Mission Owner + next session | SPIKE-01 on bench hardware BEFORE relying on containment; fallback: containment claims downgraded, OT payloads blocked until solved | SPIKE-01 result |
| RR-04 | Headend strangler stalls half-done, worst of both worlds (S-04) | M | M | Operator | ratchet metrics public per release; each extraction independently shippable; delegation shims small | ratchet flat 2 releases |
| RR-05 | Evidence debt inherited (backup/restore, mTLS, pentest) (S-05) | H | H | Operator | stage 2 makes restore drill a release gate; mTLS stage 3; external pentest before first Internet exposure | go-live date set |
| RR-06 | Solo-operator bus factor (S-06) | H | H | Mission Owner | machine-enforced invariants over vigilance; runbooks with last-exercised dates; docs in English post-migration widen the help pool | any second contributor |
| RR-07 | No hardware root of trust on edge SBC; device key theft | M | M | Operator | short-lived certs + revocation (stage 3); accept residually; consider secure-element HW at next fleet refresh | fleet hardware refresh |
| RR-08 | Single headend SPOF | M | M | Operator | evidenced restore (RTO ≤ 1 day) instead of HA — proportionality; revisit at customer SLA demand | first SLA-bearing contract |
| RR-09 | GDPR exposure while lab carries live customer data pre-migration | M | H | Mission Owner (controller/processor role unresolved) | stage 2 GDPR pack front-loaded; DPA templates before first commercial site | first commercial customer |
| RR-10 | Meta Review divergence: other reviewers propose incompatible structures | M | L | Mission Framework | traceability + refinement-level (not revolution-level) deviations keep this branch mergeable piecewise | meta review |
| RR-11 | AI-session drift re-introduces monolith habits | M | M | Operator + gates | import-boundary/secure-router/ratchet tests fail CI on drift; session boot from machine-readable invariants | recurring gate failures |
| RR-12 | Signing key compromise (policy/OTA/payload chain) | L | H | Operator | key separation (node/policy/release), offline root procedure, revocation drill documented; HMAC slice upgraded to asymmetric in stage 1 | any key event |

## Assumptions register (consolidated)

A-01..A-07 (INTAKE), A-08..A-10 (baseline evaluation). All remain open except A-01 (validated). Most consequential: **A-03/A-05** (one-operator economy; running system must keep working) — if either is wrong, proportionality calls throughout this submission should be revisited.

## Unresolved questions

Q-01..Q-04 (INTAKE §4) — none blocked the review; each carries a documented default. Additional open decision surfaced during design: **blob transport evolution** (SFTP wrapper → HTTPS channel endpoint timing, stage 2) is left to implementation-time measurement, both options behind the same `DataChannel` seam.
