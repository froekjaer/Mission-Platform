# AI & Capability Allocation Model

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Rule (retained from source ADR-001, formalised)

AI is allocated **by purpose, not as a module**. The calling domain owns purpose, prompts, data classification, provider choice, result ownership and retention. Provider adapters (Gemini, Ollama, future) are shared technical infrastructure with no ownership of anything.

## 2. AI register (v1 — current uses)

| Use | Domain owner | Data in | Provider | Result owner | Risk class (AI Act) |
|---|---|---|---|---|---|
| Image tagging | timelapse payload | customer imagery (personal-images) | Gemini Vertex EU / batch | customer archive | minimal/limited |
| Edge image QA | timelapse payload | imagery, on-node | local (NPU/Ollama) | operational | minimal |
| Tag label translation | timelapse payload | tag vocabulary | local Ollama | vocabulary | minimal |
| Ops/SIEM triage assist | platform | operational logs (no personal data by schema) | local Ollama | operator | minimal |
| Development/architecture sessions | Mission Owner governance | repo + docs | Claude/Codex | Mission Owner | out of product scope; governed by collaboration model |

New AI use = new register row + classification check; imagery to non-EU providers requires explicit mission policy (default deny).

## 3. Capability allocation across contributor types

Runtime capabilities: see business-architecture §5 (platform vs. payload vs. human authority). Development capabilities: see `docs/collaborative-intelligence.md` — humans hold final authority and all irreversible actions; AI systems produce designs, code, tests and evidence under machine-enforced gates; specialist tools (SAST, SBOM, schema validators) guard invariants that neither humans nor LLMs reliably guard by attention alone.

## 4. Guardrails

No AI writes to production systems directly; AI-proposed changes land as commits gated by CI architecture tests; AI sessions boot from the machine-readable invariants (contracts, schemas, gates) rather than prose alone — reducing the drift class documented in the source project's handover history.
