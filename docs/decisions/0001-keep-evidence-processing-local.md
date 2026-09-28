# ADR 0001: Keep evidence processing local

- Status: accepted
- Date: 2026-09-28

## Context

EvidenceIQ handles media, extracted metadata, PII, and audit records. Its documented privacy
boundary keeps that material on infrastructure controlled by the operator and uses local Ollama
models by default.

Jev is a hosted decision model. Its API accepts application state and typed questions at a remote
endpoint, requires an API key, and returns probabilistic decisions. That is useful for bounded
routing and triage, but sending EvidenceIQ content would add an external data processor and make
the current local-first claim conditional.

## Decision

Do not integrate Jev into evidence ingestion, classification, search, reporting, authorization, or
PII handling. Existing deterministic authorization and local models remain the correct boundary.

Jev may be reconsidered only for non-sensitive operational data after there is a concrete use case,
a privacy and retention review, an explicit opt-in deployment mode, confidence thresholds, a safe
fallback, and human review for consequential decisions. Model output must never grant permission.

## References

- [Jev API reference](https://docs.typesafe.ai/api)
- [Jev state concepts](https://docs.typesafe.ai/concepts/state)

