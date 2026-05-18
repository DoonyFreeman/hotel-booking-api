.PHONY: dev test lint migrate seed docker-up docker-down docker-rebuild mon-up mon-down mon-logs dev-metrics

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
	docker compose up alertmanager prometheus grafana postgres_exporter redis_exporter nginx_exporter -d

mon-down:
	docker compose down alertmanager prometheus grafana postgres_exporter redis_exporter nginx_exporter

mon-logs:
	docker compose logs -f alertmanager prometheus grafana postgres_exporter redis_exporter nginx_exporter

dev-metrics:
	@echo "=== Local dev with monitoring stack ==="
	@echo ""
	@echo "Run in separate terminals:"
	@echo "  Terminal 1: make dev               # FastAPI на localhost:8000"
	@echo "  Terminal 2: make mon-up            # мониторинг в Docker"
	@echo ""
	@echo "Prometheus будет скрапить booking_back:8000 (Docker mode)."
	@echo "Для локального режима нужно указать target host.docker.internal:8000:"
	@echo "  cp prometheus/prometheus-local.yml prometheus/prometheus.yml"
	@echo "  docker compose up prometheus grafana ... -d"
