# Gorgias MCP Server Makefile

.PHONY: help install test lint clean run-mcp run-cloud-run

help: ## Show this help message
	@echo "Gorgias MCP Server - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run all tests
	python test_ci.py

test-local: ## Run local tests with real credentials
	python test_setup.py

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

run-mcp: ## Run MCP server locally (stdio mode)
	python -m src.server

run-cloud-run: ## Run Cloud Run server locally
	python cloud_run_mcp.py

run-example: ## Run example usage
	python example_usage.py

ci: install test lint ## Run full CI pipeline locally

deploy-test: ## Test deployment configuration
	@echo "Testing Cloud Run configuration..."
	python -c "import json; json.load(open('mcp_config.json')); print('✅ mcp_config.json valid')"
	python -c "import yaml; yaml.safe_load(open('cloudbuild.yaml')); print('✅ cloudbuild.yaml valid')"
	@echo "✅ Deployment configuration is valid"

monitor-ci: ## Monitor CI/CD deployment status
	@./monitor-ci.sh --once

monitor-ci-live: ## Monitor CI/CD deployment status (continuous)
	@./monitor-ci.sh

monitor-workflow: ## Monitor a specific GitHub Actions workflow run
	@./monitor-workflow.sh $(WORKFLOW_ID)

monitor-builds: ## Monitor GitHub Actions builds for new commits until success
	@./monitor-builds.sh $(BRANCH)
