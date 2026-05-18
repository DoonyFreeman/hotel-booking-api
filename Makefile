.PHONY: dev test lint migrate seed docker-up docker-down mon-up mon-down mon-logs dev-metrics

dev:
	uvicorn src.main:app --reload --host 0.0.0.0

test:
	pytest -v --tb=short

lint:
	ruff check src/ tests/

migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(name)"

seed:
	python seed_data.py

docker-up:
	docker compose up

docker-down:
	docker compose down

docker-rebuild:
	docker compose down && docker compose up --build

mon-up:
	docker compose up prometheus grafana postgres_exporter redis_exporter nginx_exporter -d

mon-down:
	docker compose down prometheus grafana postgres_exporter redis_exporter nginx_exporter

mon-logs:
	docker compose logs -f prometheus grafana postgres_exporter redis_exporter nginx_exporter

dev-metrics:
	@echo "FastAPI local (venv) + monitoring stack in Docker"
	@echo "Run 'make dev' in another terminal, then:"
	@echo "  docker compose up prometheus grafana postgres_exporter redis_exporter nginx_exporter -d"
