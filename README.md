# Shield Aegis - Secure AI Agent Platform

> **The AI agent your security team won't hate.**

Aegis is an open-source, self-hosted AI agent platform built on LangGraph and Anthropic Claude. It delivers the power of autonomous AI agents with enterprise-grade security built in - not bolted on.

## Features

- LangGraph Agent powered by Claude claude-sonnet-4-5
- Live Web Search via DDGS
- AES-256 Encrypted Memory with per-user keys
- HashiCorp Vault - zero secrets in env files
- OPA Policy Engine - pre-execution allowlist
- Tamper-evident Audit Logging
- Browser Dashboard - chat, audit, memory
- Docker Compose - one-command deployment
- GDPR Ready - right-to-erasure built in

## Architecture

Request -> nginx Gateway -> OPA Policy -> LangGraph Agent -> Encrypted Memory -> Vault

## Quick Start

Prerequisites: Docker Desktop, Python 3.11+, Anthropic API Key

    git clone https://github.com/Indianinnovation/aegis.git
    cd aegis
    cp .env.example .    cp .env.example .    cp .env.example ml
    pyt    pyt  d/    pyt    pyt  d/    pyt    pyt  d/    
                                                  er

- Landing page:  http://localhost
- Dashboard:     http://localhost/dashboard.html
- Vault UI:      http://localhost:8200

## Chat with Your Agent

    curl -X POST http://localhost/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "Search the web for latest O-RAN news"}'

## Security Model

| Threat | Protection |
|---|---|
| Prompt injection | OPA blocklist pre-execution |
| Memory exposure | AES-256 encryption per-user |
| API key theft | HashiCorp Vault only |
| Untracked actions | Tamper-evident JSONL audit log |
| Brute force | JWT auth + rate limiting | Brute force s || Brute force | JWT auth + rate limiting | Brute force s || Brute force | JWT auth |---|| Brute|
| Setup| Setup| Setup| Setup| Setup| Setup| Setup| Setup| Setup| S
| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me|s || Me| Me| og | Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me|se || Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me|ec| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Me| Murity.py    - Vault, encryption, audit, policy
        main.py             - FastAPI + LangGraph agent
        config.yaml         - Agent configuration
        requirements.txt
    nginx/
                                                   html/dashboard.html - Chat dashboard
        nginx.conf
    opa/policy.rego         - Security policies
    wizard/setup_wizard.py  - Interactive setup
    docker-compose.yml
    .env.example

## Useful Commands

    docker compose logs -f agent     # View agent logs
    curl http://localhost/audit      # Check audit log
    curl http://localhost/memories   # View memories
    curl -X DELETE http://localhost/memories  # Purge memories
    docker compose restart agent     # Restart agent
    docker compose down              # Stop everything

## Tech Stack

- Agent Runtime: LangGraph + Anthropic Claude
- API Gateway: nginx + FastAPI
- Policy Engine: Open Policy Agent
- Secrets: HashiCorp Vault
- Memory: SQLite + AES-256
- Search: DDGS
- Queue: Redis
- Containers: Docker Compose

## Contributing

1. Fork the repo
2. Create branch: git checkout -b feature/my-skill
3. Commit: git commit -m "Add my skill"
4. Push: git push origin feature/my-skill
5. Open a Pull Re5. Open a Pull Re5. Open a Pull Re5. Open a Pull Re5. Open a Pull Re5. Opimization / AI Platform Engineer
- GitHub: https://github.com/Indianinnovation
- L- L- L- L- L- L- L- L- L- L- L- L- L- L- L- L-r-- L- L- L- L- L- L- L AI agent your security team won't hate*
