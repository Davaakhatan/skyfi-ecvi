.PHONY: help install dev test format lint migrate upgrade downgrade run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make test       - Run tests"
	@echo "  make format     - Format code with black and ruff"
	@echo "  make lint       - Lint code with ruff and mypy"
	@echo "  make migrate    - Create new migration"
	@echo "  make upgrade    - Run database migrations"
	@echo "  make downgrade  - Rollback last migration"
	@echo "  make run        - Run development server"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest

format:
	black app/
	ruff check --fix app/

lint:
	ruff check app/
	mypy app/

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

