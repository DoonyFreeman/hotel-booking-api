# Booking API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136.1-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.4-DC382D)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.6-37814A)](https://docs.celeryproject.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://www.docker.com/)

Асинхронный REST API для бронирования отелей. Пет-проект, демонстрирующий
промышленный подход к построению бэкенда на Python.

**Проблема:** типичный учебный проект — это монолит с синхронными запросами,
без фоновых задач, кэширования и тестов. Он ложится под первой же нагрузкой.

**Что делает этот проект:** реализует полноценный бэкенд системы бронирования
с регистрацией, поиском отелей по датам, управлением номерами, бронированиями, —
всё асинхронно, с изоляцией слоёв, без блокировок I/O.

**Какие проблемы решает архитектура:**

- **Производительность** — async/await во всём стеке (FastAPI + SQLAlchemy 2.0 +
  asyncpg). Ни один запрос не блокирует event loop.
- **Тяжёлые операции вне request-response** — Celery выносит ресайз изображений
  и будущие email-рассылки в фоновые воркеры. API отвечает мгновенно.
- **Горячие эндпоинты не долбят БД** — список отелей и удобств кэшируется в Redis
  (fastapi-cache2, TTL 10s).
- **Безопасность** — пароли через bcrypt с солью, JWT в HTTP-only cookie
  (недоступен JS), схемы Request → Internal → Response исключают утечку полей.
- **БД под контролем** — Alembic версионирует схему, 7 миграций от первой
  таблицы до связей M2M.
- **Инфраструктура за минуту** — Docker Compose поднимает 6 сервисов одной
  командой: Postgres 16, Redis 7, Nginx с rate limiting, Celery Worker + Beat.
- **Тесты не трогают реальные данные** — отдельная `DB_NAME=test` через
  `.env-test`, изолированные fixtures, мок кэша.
- **Слой Repository + DataMapper** — SQLAlchemy не протекает в бизнес-логику.
  ORM-модели не покидают слой данных, наружу идут только Pydantic-схемы.

## Tech Stack

| Технология | Проблема | Решение |
|-----------|----------|---------|
| **FastAPI** | Синхронный REST фреймворк блокирует I/O | Async endpoints через `async/await`, автодокументация OpenAPI/Swagger |
| **SQLAlchemy 2.0 + asyncpg** | ORM блокирует event loop | Асинхронный движок + пул соединений, typed ORM-запросы |
| **Alembic** | Ручное управление схемой БД | Версионирование миграций, авто-генерация из моделей |
| **Pydantic V2** | Валидация на каждом слое вручную | Схемы RequestAdd → Add → Response с разделением ответственности |
| **Celery + Redis** | Тяжёлые операции (resize image, email) в request-response | Асинхронная очередь задач + периодический Celery Beat |
| **fastapi-cache2 + Redis** | Повторные одинаковые запросы к БД | Кэш с TTL 10с для горячих эндпоинтов (отели, удобства) |
| **JWT + bcrypt** | Хранение сессий на сервере | Stateless auth через HTTP-only cookie, Hash паролей с солью |
| **Repository Pattern + DataMapper** | SQLAlchemy протекает в бизнес-логику | Изоляция ORM: API → Service → Repository → DB, Mapper конвертирует ORM → Pydantic |
| **Nginx (rate limiting)** | Нет защиты от брутфорса | 10 запросов/сек на IP через `limit_req_zone` |
| **Pillow** | Клиентские изображения разного размера | Ресайз 3 варианта (200/500/1000px) в фоне через `BackgroundTasks` |
| **Docker Compose** | Ручной запуск 6 сервисов | Одна команда — Postgres, Redis, API, Celery Worker, Celery Beat, Nginx |

## Quick Start

### 1. Скопируй `.env.example` в `.env`

```bash
cp .env.example .env
# Для Docker: открой .env и замени DB_HOST=booking_db, REDIS_HOST=booking_cache
```

Все настройки в одном файле. `docker compose` сам подхватит переменные для Postgres,
Redis и приложения — дублирования нет.

### 2. Запусти

#### Docker (рекомендуется)

```bash
docker compose up
docker exec booking_back python -m alembic upgrade head
```

- API напрямую: http://localhost:7777/docs
- Через Nginx (rate limit 10 r/s): http://localhost:80/docs

#### Локально

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```

Фоновые задачи (отдельные терминалы):

```bash
celery -A src.tasks.celery_app worker -l INFO
celery -A src.tasks.celery_app beat -l INFO
```

### 3. (Опционально) Заполни тестовыми данными

```bash
python seed_data.py
```

## API

| Method | Path | Auth | Описание |
|--------|------|------|----------|
| POST | `/auth/register` | — | Регистрация (email + password) |
| POST | `/auth/login` | — | Вход, JWT в HTTP-only cookie |
| GET | `/auth/me` | Cookie | Текущий пользователь |
| GET | `/auth/logout` | — | Очистка cookie |
| GET | `/hotels` | — | Список отелей (cached 10s, фильтры: location, title, dates, пагинация) |
| GET | `/hotels/{id}` | — | Отель |
| POST | `/hotels` | — | Создать отель |
| PATCH | `/hotels/{id}` | — | Частичное обновление |
| DELETE | `/hotels/{id}` | — | Удалить |
| GET | `/hotels/{id}/rooms` | — | Номера отеля с доступностью (query: date_from, date_to) |
| POST | `/hotels/{id}/rooms` | — | Создать номер (с facilities_ids) |
| GET | `/hotels/{id}/rooms/{rid}` | — | Номер с удобствами |
| PATCH | `/hotels/{id}/rooms/{rid}` | — | Частичное обновление номера |
| DELETE | `/hotels/{id}/rooms/{rid}` | — | Удалить номер |
| GET | `/bookings` | — | Все бронирования |
| GET | `/bookings/me` | Cookie | Мои бронирования |
| POST | `/bookings` | Cookie | Создать бронь (room_id, date_from, date_to) |
| GET | `/facilities` | — | Удобства (cached 10s) |
| POST | `/facilities` | — | Создать удобство |
| POST | `/images` | — | Загрузить изображение (multipart, ресайз в фоне) |

## Architecture

```
Request → API Layer (router) → Service Layer (business logic)
                                     ↓
                              Repository Layer (data access)
                                     ↓
                              ORM Models (SQLAlchemy)
                                     ↓
                              PostgreSQL (asyncpg)
```

**Layered schemas (трёхуровневая валидация):**

```
*RequestAdd  — что шлёт клиент (например, BookingAddRequest: room_id, date_from, date_to)
     ↓
*Add         — что идёт в БД (BookingAdd: + user_id из JWT, + price из БД)
     ↓
*            — что возвращается клиенту (Booking: + id, from_attributes=True)
```

Это гарантирует, что клиент не отправит `user_id` или `price`, и не получит `hashed_password`.

## Project Structure

```
src/
├── main.py               # FastAPI app, lifespan (Redis, cache init)
├── config.py             # Pydantic Settings из .env
├── database.py           # async engine, sessionmaker, Base
├── exceptions.py         # Domain + HTTP exceptions
├── api/                  # Route handlers (auth, hotels, rooms, bookings, ...)
├── services/             # Business logic (AuthService, HotelService, ...)
├── repositories/         # Data access (CRUD, сложные запросы)
│   └── mappers/          # ORM → Pydantic converters
├── models/               # SQLAlchemy ORM models
├── schemas/              # Pydantic validation schemas
├── tasks/                # Celery config + task definitions
├── connectors/           # Redis async connector
├── migrations/           # Alembic migrations (7 files)
└── static/images/        # Uploaded + resized images
tests/
├── unit_tests/           # Unit: JWT creation
└── integration_tests/    # Integration: auth flow, hotels, bookings, facilities
```

## Environment Variables

Все переменные задаются в `.env`. Docker Compose использует их для Postgres и Redis
через `${}` интерполяцию — не нужно дублировать значения.

Шаблон: `.env.example` → копируешь в `.env`, правишь под себя.

| Variable | Пример | Описание |
|----------|--------|----------|
| `DB_HOST` | `booking_db` / `localhost` | Хост Postgres (Docker / локально) |
| `DB_PORT` | `5432` | Порт Postgres |
| `DB_USER` | `postgres` | Пользователь Postgres |
| `DB_PASS` | `postgres` | Пароль Postgres |
| `DB_NAME` | `booking` | Имя БД |
| `REDIS_HOST` | `booking_cache` / `localhost` | Хост Redis |
| `REDIS_PORT` | `6379` | Порт Redis |
| `JWT_SECRET_KEY` | `change-me` | Секрет для JWT (для прода — сгенерируй свой) |
| `JWT_ALGORITHM` | `HS256` | Алгоритм JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни токена (мин) |

## DB Schema

```
users (id, email*, hashed_password)
  └── bookings (id, user_id*, room_id*, date_from, date_to, price)
hotels (id, title, location)
  └── rooms (id, hotel_id*, title, description, price, quantity)
        └── rooms_facilities (id, room_id*, facility_id*)
facilities (id, title)
```

M2M: `rooms` ↔ `facilities` через `rooms_facilities`.

---

## Мониторинг (Prometheus + Grafana)

FastAPI автоматически экспортирует метрики на `/metrics`. Prometheus собирает их
вместе с метриками PostgreSQL, Redis и Nginx. Grafana визуализирует дашборды.

```
                          ┌──────────────┐
                          │   Grafana    │
                          │   :3000      │
                          └──────┬───────┘
                                 │ queries
                          ┌──────▼───────┐
                          │  Prometheus  │
                          │  :9090       │
                          └──┬──┬──┬─────┘
                             │  │  │
                  scrape     │  │  │
      ┌──────────────────────┘  │  └─────────────────────┐
      │                         │                        │
   ┌──▼──────────┐   ┌─────────▼────┐   ┌───────────────▼──┐
   │  FastAPI    │   │  postgres    │   │   redis         │
   │  /metrics   │   │  _exporter   │   │   _exporter     │
   │  :8000      │   │  :9187       │   │   :9121         │
   └─────────────┘   └──────────────┘   └──────────────────┘
```

### Port Mapping

| Сервис | Внутренний порт | Внешний порт |
|---|---|---|
| FastAPI (напрямую) | 8000 | 7777 |
| Nginx | 80 | 80 |
| Prometheus | 9090 | 9090 |
| Grafana | 3000 | 3000 |
| Alertmanager | 9093 | 9093 |
| Postgres Exporter | 9187 | 9187 |
| Redis Exporter | 9121 | 9121 |
| Nginx Exporter | 9113 | 9113 |

### Запуск мониторинга

#### Docker (все сервисы, рекомендуется)

Всё уже в `docker compose up` — Prometheus, Grafana, Alertmanager и экспортеры
запускаются вместе с API. Открой:

| Ссылка | Описание |
|--------|----------|
| http://localhost:3000 | Grafana (admin / admin) |
| http://localhost:9090 | Prometheus |
| http://localhost:7777/docs | API напрямую |
| http://localhost:80/docs | API через Nginx |

#### Локально (venv + Docker)

FastAPI в `venv`, мониторинг в Docker:

```bash
# Терминал 1:
make dev                                   # FastAPI на localhost:8000

# Терминал 2:
make mon-up                                # Prometheus + Grafana + экспортеры
```

Prometheus скрапит `host.docker.internal:8000`. При первом запуске убедись,
что в `prometheus/prometheus.yml` target = `['host.docker.internal:8000']`.

```bash
make dev-metrics                            # подсказка
cp prometheus/prometheus-local.yml prometheus/prometheus.yml  # переключить
make mon-up
```

### Дашборды

#### `FastAPI Metrics` — http://localhost:3000/d/fastapi-metrics

![FastAPI Dashboard](grafana/screenshots/fastapi_dashboard.png)

| Панель | Что показывает | PromQL |
|--------|---------------|--------|
| **RPS** | Запросов в секунду по эндпоинтам | `rate(http_requests_total[1m])` |
| **P50 / P95 / P99 Latency** | Задержка запросов (50-й, 95-й, 99-й перцентиль) | `histogram_quantile(0.5/0.95/0.99, rate(http_request_duration_seconds_bucket[5m]))` |
| **Status Codes** | Распределение 2xx, 4xx, 5xx | `http_requests_total{status=~"2.."}` и т.д. |
| **Active Requests** | Текущие активные запросы | `http_requests_in_progress` |
| **Business** | Созданные бронирования, зарегистрированные пользователи | `bookings_created_total`, `users_registered_total` |

**P50 / P95 / P99 — что это значит:**
- **P50 (медиана)** — типичная задержка. Половина запросов быстрее, половина — медленнее.
- **P95** — 95% запросов быстрее этого значения. Стабильность системы для большинства пользователей.
- **P99** — 99% запросов быстрее. Выявляет выбросы — 1 из 100 запросов аномально медленный.

Если P50 = 50ms, P95 = 200ms, P99 = 2s — в среднем всё хорошо, но 1% запросов
тормозит. Резкий рост P99 без роста P50 часто указывает на проблемы с БД, Redis
или GC паузы.

#### `DDoS / Security` — http://localhost:3000/d/ddos-security

![DDoS Dashboard](grafana/screenshots/ddos_dashboard.png)

| Панель | Что показывает | PromQL |
|--------|---------------|--------|
| **RPS Timeline** | Общий RPS + порог (1000 req/s) | `sum(rate(http_requests_total[1m]))` |
| **Error Rate** | Доля 5xx от всех запросов + порог (5%) | `sum(rate(...{status=~"5.."})) / sum(rate(...))` |
| **P95 Latency** | P95 задержка + порог (2s) | `histogram_quantile(0.95, ...)` |
| **Nginx Connections** | Активные соединения Nginx + порог (500) | `nginx_connections_active` |
| **Top Endpoints** | Топ-10 эндпоинтов по нагрузке | `topk(10, sum by (path) (rate(...)))` |

### Alerting (Prometheus Alertmanager)

4 правила алертинга для автоматического обнаружения DDoS и проблем:

| Alert | Выражение | Severity |
|-------|-----------|----------|
| HighRequestRate | RPS > 1000 за 1 мин | warning |
| LatencySpike | P95 latency > 2s за 2 мин | warning |
| HighErrorRate | 5xx > 5% за 2 мин | critical |
| NginxConnSpike | nginx_connections_active > 500 | warning |

Проверить активные алерты:

```bash
curl http://localhost:9090/api/v1/alerts
curl http://localhost:9093/api/v2/alerts
```

### Бизнес-метрики

В коде инкрементятся кастомные счётчики:

| Метрика | Где инкрементится | Метки |
|---------|------------------|-------|
| `bookings_created_total` | `services/bookings.py:add_booking` | `hotel_id` |
| `bookings_cancelled_total` | `services/bookings.py:cancel_booking` | — |
| `users_registered_total` | `services/auth.py:register_user` | — |

### Docker Compose Services (полный список)

| Контейнер | Образ | Назначение |
|-----------|-------|------------|
| `booking_db` | postgres:16 | База данных |
| `booking_cache` | redis:7.4 | Кэш + Celery broker |
| `booking_back` | booking_back FastAPI | API (uvicorn) |
| `booking_nginx` | nginx:latest | Reverse proxy + rate limiting |
| `booking_celery_worker` | booking_back | Celery worker (ресайз изображений) |
| `booking_celery_beat` | booking_back | Celery beat (периодические задачи) |
| `booking_prometheus` | prom/prometheus | Сбор метрик |
| `booking_alertmanager` | prom/alertmanager | Alerting |
| `booking_grafana` | grafana/grafana | Визуализация |
| `booking_pg_exporter` | prometheuscommunity/postgres-exporter | Метрики PostgreSQL |
| `booking_redis_exporter` | oliver006/redis_exporter | Метрики Redis |
| `booking_nginx_exporter` | nginx/nginx-prometheus-exporter | Метрики Nginx |

### Makefile таргеты для мониторинга

```bash
make mon-up        # Запустить Prometheus + Grafana + экспортеры + Alertmanager
make mon-down      # Остановить мониторинг
make mon-logs      # Логи мониторинга
make dev-metrics   # Подсказка для локального сценария
```

### Безопасность

- `/metrics` **закрыт через Nginx** (HTTP 403 снаружи) — доступен только внутри Docker сети
  напрямую к FastAPI (`booking_back:8000`)
- `/nginx-status` закрыт по `allow/deny` — только Docker подсеть
- Prometheus и Grafana не публикуются в production (сейчас открыты для отладки)
- Postgres exporter использует read-only пользователя `exporter` с `pg_read_all_stats`