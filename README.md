# Shield Aegis — Secure AI Agent Platform

> **The AI agent your security team won't hate.**

Aegis is an open-source, self-hosted AI agent platform built on LangGraph and Anthropic Claude. It delivers the power of autonomous AI agents with enterprise-grade security built in — not bolted on.

## Features

- LangGraph agent powered by Claude claude-sonnet-4-5
- Live web search via DDGS
- AES-256 encrypted memory with per-user keys
- HashiCorp Vault — zero secrets in env files
- OPA policy engine — enforced pre-execution on every tool call
- Tamper-evident audit logging (JSONL)
- Browser dashboard — chat, audit, memory
- Docker Compose — one-command deployment
- GDPR ready — right-to-erasure built in

## Architecture

```
Request → nginx Gateway → FastAPI Agent → OPA Policy Check → LangGraph Tools → Encrypted Memory
                                                                      ↓
                                                               Audit Log (JSONL)
```

## Quick Start

**Prerequisites:** Docker Desktop, Python 3.11+, Anthropic API key

```bash
git clone https://github.com/Indianinnovation/aegis.git
cd aegis

# Interactive setup — writes .env and agent/config.yaml
python wizard/setup_wizard.py

# Start all services
docker compose up -d
```

- Landing page:  http://localhost
- Dashboard:     http://localhost/dashboard.html
- Vault UI:      http://localhost:8200

## Manual Setup (without wizard)

```bash
cp .env.example .env
# Edit .env and fill in all values, then:
docker compose up -d
```

## Chat with Your Agent

```bash
curl -X POST http://localhost/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search the web for latest O-RAN news"}'
```

## Security Model

| Threat | Protection |
|---|---|
| Prompt injection | OPA blocklist enforced before every tool call |
| Memory exposure | AES-256 encryption per-user key (scrypt-derived) |
| API key theft | HashiCorp Vault — never in env files |
| Untracked actions | Tamper-evident JSONL audit log |
| Weak encryption key | Hard startup failure if `MEMORY_MASTER_KEY` is missing or default |
| Hardcoded secrets | All secrets sourced from `.env` — none in `docker-compose.yml` |
| Abuse / flooding | nginx rate limiting — 10 req/min on `/chat`, 30 req/min on `/api/` |

## Project Structure

```
aegis/
├── agent/
│   ├── core/
│   │   └── security.py       # Vault, AES-256 memory, audit logger
│   ├── skills/
│   │   └── websearch.py      # Web search skill (LangChain tool)
│   ├── config.yaml           # Agent name, model, timezone, skills
│   ├── Dockerfile
│   ├── main.py               # FastAPI + LangGraph agent + OPA enforcement
│   └── requirements.txt
├── nginx/
│   ├── html/
│   │   ├── index.html
│   │   └── dashboard.html    # Chat dashboard
│   └── nginx.conf
├── opa/
│   └── policy.rego           # Security policies (tool blocklist)
├── wizard/
│   └── setup_wizard.py       # Interactive first-time setup
├── worker/
│   └── worker.py             # Background Redis queue worker
├── docker-compose.yml
└── .env.example
```

## Environment Variables

All secrets are required. Copy `.env.example` to `.env` and fill in every value, or run the setup wizard.

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `VAULT_TOKEN` | HashiCorp Vault dev root token |
| `REDIS_PASSWORD` | Redis auth password |
| `MEMORY_MASTER_KEY` | 64-char hex key for AES-256 memory encryption |

Generate a secure memory key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Useful Commands

```bash
docker compose logs -f agent          # View agent logs
docker compose restart agent          # Restart agent

curl http://localhost/audit           # View audit log
curl http://localhost/memories        # View memories
curl -X DELETE http://localhost/memories  # Purge memories (GDPR erasure)

docker compose down                   # Stop everything
```

## Tech Stack

| Component | Technology |
|---|---|
| Agent runtime | LangGraph + Anthropic Claude |
| API | FastAPI + nginx |
| Policy engine | Open Policy Agent (OPA) |
| Secrets | HashiCorp Vault |
| Memory | SQLite + AES-256 (Fernet) |
| Search | DDGS |
| Queue | Redis |
| Containers | Docker Compose |

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-skill`
3. Commit: `git commit -m "Add my skill"`
4. Push: `git push origin feature/my-skill`
5. Open a Pull Request

## Author

Built by Dilip R Tandekar — AI Solution Architect 
- GitHub: https://github.com/Indianinnovation
- LinkedIn: https://linkedin.com/in/dilip-tandekar-00419a6


---

*The AI agent your security team won't hate.*
