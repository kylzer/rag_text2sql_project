.PHONY: run stop clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

run: ## Start everything
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python3.10 -m venv $(VENV); \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r requirements.txt; \
	fi
	@echo "Starting Docker services..."
	@docker-compose up -d --build
	@echo "Starting Gradio..."
	@$(PYTHON) main.py

stop: ## Stop everything
	@docker-compose down
	@echo "Stopped"

clean: ## Clean everything
	@docker-compose down -v
	@rm -rf $(VENV)
	@rm -rf database/vectorRepo.db
	@rm -rf database/data.db
	@rm -rf database/db_schema.json
	@echo "Cleaned"