.PHONY: schema
schema:
	@poetry run python scripts/generate_schema.py

.PHONY: format
format:
	@poetry run black backend

.PHONY: lint
lint:
	@poetry run pylint backend
