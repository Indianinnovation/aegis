#!/usr/bin/env python3
"""Aegis Setup Wizard - interactive first-time configuration."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def prompt(label: str, default: str = "", secret: bool = False) -> str:
    display = f"[{default}]" if default and not secret else ""
    suffix = f" {display}: " if display else ": "
    try:
        if secret:
            import getpass
            val = getpass.getpass(f"  {label}{suffix}")
        else:
            val = input(f"  {label}{suffix}").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return val or default


def write_env(api_key: str, vault_token: str, redis_password: str, memory_key: str):
    env_path = ROOT / ".env"
    env_path.write_text(
        f"ANTHROPIC_API_KEY={api_key}\n"
        f"VAULT_TOKEN={vault_token}\n"
        f"REDIS_PASSWORD={redis_password}\n"
        f"MEMORY_MASTER_KEY={memory_key}\n"
        f"SECRET_BACKEND=env\n"
    )
    print(f"  ✓ Written: {env_path}")


def write_config(name: str, user: str, model: str, timezone: str):
    config_path = ROOT / "agent" / "config.yaml"
    config_path.write_text(
        f"agent:\n"
        f"  model: {model}\n"
        f"  name: {name}\n"
        f"  provider: anthropic\n"
        f"  timezone: {timezone}\n"
        f"  user: {user}\n"
        f"channels:\n"
        f"  web_ui:\n"
        f"    enabled: true\n"
        f"heartbeat:\n"
        f"  enabled: false\n"
        f"  morning_briefing: 0 8 * * *\n"
        f"security:\n"
        f"  audit_logging: true\n"
        f"  memory_encryption: true\n"
        f"  require_confirmation: High-risk only\n"
        f"skills:\n"
        f"  websearch:\n"
        f"    enabled: true\n"
    )
    print(f"  ✓ Written: {config_path}")


def main():
    print("\n╔══════════════════════════════════╗")
    print("║   Aegis Setup Wizard             ║")
    print("╚══════════════════════════════════╝\n")

    print("── Agent Identity ──")
    user = prompt("Your name", "User")
    agent_name = prompt("Agent name", f"{user}'s Aegis Assistant")
    timezone = prompt("Timezone", "America/New_York")
    model = prompt("Claude model", "claude-sonnet-4-5")

    print("\n── Secrets ──")
    api_key = prompt("Anthropic API key (sk-ant-...)", secret=True)
    if not api_key.startswith("sk-"):
        print("  ⚠ Warning: key doesn't look like an Anthropic key")

    vault_token = prompt("Vault dev token", secret=True)
    redis_password = prompt("Redis password", secret=True)

    import secrets as _s
    default_mem_key = _s.token_hex(32)
    memory_key = prompt("Memory master key (leave blank to auto-generate)", default_mem_key)

    print("\n── Writing configuration ──")
    write_env(api_key, vault_token, redis_password, memory_key)
    write_config(agent_name, user, model, timezone)

    print("\n✅ Setup complete! Run:\n")
    print("   docker compose up -d\n")
    print("   Then open http://localhost/dashboard.html\n")


if __name__ == "__main__":
    main()
