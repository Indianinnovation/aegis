# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| latest (main) | ✅ |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately via GitHub's Security Advisory feature:
1. Go to the [Security tab](https://github.com/Indianinnovation/aegis/security/advisories/new)
2. Click "Report a vulnerability"
3. Fill in the details

Or email directly via the GitHub profile contact.

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within 48 hours. If confirmed, a fix will be released within 7 days for critical issues.

## Security Design

Aegis is built with defence-in-depth:

| Layer | Control |
|---|---|
| Gateway | nginx rate limiting — 10 req/min on `/chat` |
| Policy | OPA enforced pre-execution on every tool call |
| Secrets | HashiCorp Vault — no keys in env files |
| Memory | AES-256 encryption with per-user scrypt-derived keys |
| Audit | Tamper-evident JSONL log of every agent action |
| Startup | Hard failure if `MEMORY_MASTER_KEY` is missing or insecure |

## Known Limitations

- This is a **dev-mode** deployment (Vault runs in dev mode). Do not expose port 8200 publicly.
- The OPA policy blocklist covers known dangerous patterns — it is not exhaustive. Review `opa/policy.rego` and extend it for your threat model.
- Memory is encrypted at rest but decrypted in-process during recall. Protect the host accordingly.
