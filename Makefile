.DEFAULT_GOAL := help
COMPOSE := docker compose

# ── Colours ────────────────────────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
RESET  := \033[0m

# ══════════════════════════════════════════════════════════════════
##@ Setup
# ══════════════════════════════════════════════════════════════════

.PHONY: setup
setup: ## Interactive first-time setup (writes .env + config.yaml)
	@echo "$(GREEN)Running Aegis setup wizard...$(RESET)"
	@python3 wizard/setup_wizard.py

.PHONY: check
check: ## Verify prerequisites (Docker, Python, .env)
	@echo "$(GREEN)Checking prerequisites...$(RESET)"
	@command -v docker   >/dev/null 2>&1 || { echo "$(RED)✗ Docker not found. Install Docker Desktop: https://docs.docker.com/get-docker/$(RESET)"; exit 1; }
	@docker info         >/dev/null 2>&1 || { echo "$(RED)✗ Docker daemon not running. Start Docker Desktop.$(RESET)"; exit 1; }
	@command -v python3  >/dev/null 2>&1 || { echo "$(RED)✗ Python 3 not found.$(RESET)"; exit 1; }
	@python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" || { echo "$(RED)✗ Python 3.11+ required.$(RESET)"; exit 1; }
	@test -f .env        || { echo "$(RED)✗ .env not found. Run: make setup$(RESET)"; exit 1; }
	@grep -q "ANTHROPIC_API_KEY=sk-" .env || { echo "$(RED)✗ ANTHROPIC_API_KEY missing or invalid in .env$(RESET)"; exit 1; }
	@grep -q "MEMORY_MASTER_KEY=" .env    || { echo "$(RED)✗ MEMORY_MASTER_KEY missing in .env$(RESET)"; exit 1; }
	@echo "$(GREEN)✓ All prerequisites met$(RESET)"

# ══════════════════════════════════════════════════════════════════
##@ Core
# ══════════════════════════════════════════════════════════════════

.PHONY: up
up: check ## Build and start all services
	@echo "$(GREEN)Starting Aegis...$(RESET)"
	@$(COMPOSE) up -d --build
	@echo ""
	@echo "$(GREEN)✓ Aegis is running$(RESET)"
	@echo "  Dashboard → http://localhost/dashboard.html"
	@echo "  Vault UI  → http://localhost:8200"
	@echo "  Health    → http://localhost/health"

.PHONY: down
down: ## Stop all services
	@$(COMPOSE) down

.PHONY: restart
restart: ## Restart all services
	@$(COMPOSE) restart

# ══════════════════════════════════════════════════════════════════
##@ Logs
# ══════════════════════════════════════════════════════════════════

.PHONY: logs
logs: ## Tail logs for all services
	@$(COMPOSE) logs -f

.PHONY: logs-agent
logs-agent: ## Tail agent logs only
	@$(COMPOSE) logs -f agent

.PHONY: logs-nginx
logs-nginx: ## Tail nginx logs only
	@$(COMPOSE) logs -f nginx

# ══════════════════════════════════════════════════════════════════
##@ Agent
# ══════════════════════════════════════════════════════════════════

.PHONY: chat
chat: ## Send a test message to the agent
	@curl -s -X POST http://localhost/chat \
		-H "Content-Type: application/json" \
		-d '{"message":"Hello! What can you do?"}' | python3 -m json.tool

.PHONY: health
health: ## Check agent health
	@curl -s http://localhost/health | python3 -m json.tool

.PHONY: audit
audit: ## View the last 20 audit log entries
	@curl -s http://localhost/audit | python3 -m json.tool

.PHONY: memories
memories: ## View stored memories
	@curl -s http://localhost/memories | python3 -m json.tool

.PHONY: purge
purge: ## Purge all memories (GDPR erasure)
	@echo "$(YELLOW)Purging all memories...$(RESET)"
	@curl -s -X DELETE http://localhost/memories | python3 -m json.tool

# ══════════════════════════════════════════════════════════════════
##@ Development
# ══════════════════════════════════════════════════════════════════

.PHONY: rebuild
rebuild: ## Force rebuild agent image without cache
	@$(COMPOSE) build --no-cache agent
	@$(COMPOSE) up -d agent

.PHONY: ps
ps: ## Show running containers and their status
	@$(COMPOSE) ps

.PHONY: shell
shell: ## Open a shell inside the agent container
	@$(COMPOSE) exec agent /bin/bash

.PHONY: clean
clean: ## Stop services and remove volumes + images
	@echo "$(YELLOW)Removing containers, volumes and images...$(RESET)"
	@$(COMPOSE) down -v --rmi local
	@echo "$(GREEN)✓ Clean$(RESET)"

# ══════════════════════════════════════════════════════════════════
##@ Help
# ══════════════════════════════════════════════════════════════════

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(GREEN)Aegis$(RESET) — Secure AI Agent Platform\n\nUsage:\n  make $(YELLOW)<target>$(RESET)\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(GREEN)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)
	@echo ""
