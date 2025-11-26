# --- Configuration ---
ENV := production
INVENTORY := hosts
VAULT_PASS_FILE := .vault_pass
VENV_NAME = .venv

.PHONY: setup deploy migrate static restart admin-shell build-frontend edit-vault encrypt-vault decrypt-vault

# Default target runs a full deployment (code, migrations, static, restart)
default: deploy


venv:
	python3 -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/pip install -r requirements.txt

lint:
	flake8 src/

format:
	black src/
clean:
	rm -rf __pycache__ *.pyc $(VENV_NAME)
# --- Primary Targets ---

# Full initial setup, including base OS config (uses 'setup' tag)
setup:
	@echo "--- Running full initial environment setup ---"
	ansible-playbook site.yml -i $(INVENTORY) --ask-vault-pass --tags setup

# Fast deployment: Update code, run migrations, collect static, and restart (uses 'deploy' and 'activate' tags)
deploy:
	@echo "--- Running fast deployment (code, migrate, static, restart) ---"
	ansible-playbook site.yml -i $(INVENTORY) --ask-vault-pass --tags deploy,activate

# Run database migrations only (uses 'migrate' tag)
migrate:
	@echo "--- Running database migrations only ---"
	ansible-playbook site.yml -i $(INVENTORY) --ask-vault-pass --tags migrate

# Run collectstatic only (uses 'static' tag)
static:
	@echo "--- Collecting static files only ---"
	ansible-playbook site.yml -i $(INVENTORY) --ask-vault-pass --tags static

# Restart the application and web server services only (uses 'services' tag on handlers)
# Requires the handlers to have the 'services' tag as shown in the previous example.
restart:
	@echo "--- Restarting services only (Gunicorn, Nginx) ---"
	ansible-playbook site.yml -i $(INVENTORY) --ask-vault-pass --tags services

# --- Vault Management Targets ---

# Edit the secrets file securely
edit-vault:
	ansible-vault edit group_vars/$(ENV)/vault.yml

# Change the vault password (requires existing password)
rekey-vault:
	ansible-vault rekey group_vars/$(ENV)/vault.yml


admin-shell:
	@container_id=$$(docker compose ps -q web); \
	if [ -z "$$container_id" ]; then \
		echo "Web container not found"; \
		exit 1; \
	else \
		docker exec -it $$container_id /bin/bash; \
	fi

build-frontend:
	docker compose -f docker-compose-dev.yaml exec frontend npm run dist
	cp -r frontend/dist/static/* static/
	docker compose -f docker-compose-dev.yaml restart web

test:
	docker compose -f docker-compose-dev.yaml exec --env TESTING=True -T web pytest


deploy-dry:
	ansible-playbook ansible/playbook.yml -i ansible/inventory --check

deploy:
	ansible-playbook ansible/playbook.yml -i ansible/inventory  # --ask-vault-pass

dependencies:
	uv export --no-hashes --no-header --no-annotate --no-dev --format requirements.txt > requirements-dev.txt
	uv export --no-hashes --no-header --no-annotate --no-group dev --format requirements.txt > requirements.txt

#      uv export --no-hashes --format requirements-txt > requirements.txt; \
