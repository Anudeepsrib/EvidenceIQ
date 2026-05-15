# Security Policy

## Reporting Vulnerabilities

Please report suspected vulnerabilities privately to the repository owner. Do not open public issues that include exploit details, secrets, sample evidence, uploaded media, or PII.

Include:

- Affected component and version or commit.
- Reproduction steps using synthetic data.
- Impact and any observed exposure.
- Suggested remediation, if known.

## Sensitive Media Handling

EvidenceIQ is a local reference implementation for sensitive media workflows. Treat uploaded originals, redacted copies, thumbnails, reports, local databases, ChromaDB stores, logs, and Ollama model data as sensitive operational data.

Do not commit:

- `.env` files or real secrets.
- Uploaded media or extracted frames.
- Generated reports or thumbnails.
- SQLite databases, ChromaDB data, logs, or model files.

## Secrets

Generate a local `SECRET_KEY` with:

```bash
openssl rand -hex 32
```

Production startup rejects known weak placeholders and requires explicit, non-wildcard CORS origins. Rotate any key that may have been shared, logged, or committed.

## Local Demo Disclaimer

The project includes forensic-style controls such as SHA256 hashing, RBAC checks, audit events, and metadata redaction helpers. These controls are not a formal forensic, legal, HIPAA, GDPR, PCI, or chain-of-custody certification. Organizations must validate workflows with qualified legal, compliance, and security reviewers before using EvidenceIQ for regulated production evidence.

## External Services

AI inference is intended to run through local Ollama by default. Optional integrations must be explicitly configured and reviewed before use. Avoid adding telemetry, analytics, cloud AI SDKs, or outbound media transfer paths without an opt-in setting, tests, and documentation.
