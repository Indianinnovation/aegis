# Contributing to Aegis

Thanks for your interest in contributing!

## Getting Started

1. Fork the repo and clone it locally
2. Run the setup wizard: `python wizard/setup_wizard.py`
3. Start services: `docker compose up -d`
4. Verify everything works: `curl http://localhost/health`

## Making Changes

```bash
git checkout -b feature/your-feature
# make your changes
git commit -m "feat: describe your change"
git push origin feature/your-feature
# open a Pull Request
```

## Adding a Skill

Skills are LangChain tools in `agent/skills/`. Create a new file:

```python
# agent/skills/my_skill.py
from langchain_core.tools import tool

@tool
def my_skill(input: str) -> str:
    """Describe what this skill does."""
    ...
```

Then import and add it to the `tools` list in `agent/main.py`.

## Guidelines

- Keep changes minimal and focused
- Never commit `.env`, `*.db`, `*.jsonl`, or any secrets
- All tool calls must pass OPA policy — add rules to `opa/policy.rego` if needed
- Run `docker compose logs -f agent` to check for errors before submitting

## Reporting Issues

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- Relevant logs from `docker compose logs agent`
