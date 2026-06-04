# Omnichannel Messaging Solution

Единое решение для просмотра и ответа на сообщения из разных источников.

## Архитектура

- **Abstract Factory** — для создания движков сообщений
- **punq DI** — внедрение зависимостей
- **PostgreSQL** — хранение сообщений
- **FastAPI** — REST API и WebSocket
- **Polling** — получение сообщений

## Поддерживаемые каналы

- Telegram (через бота)
- Email (IMAP)

## Установка

```bash
cd /home/proudrykar/test_task

source .venv/bin/activate

poetry install

cp .env.example .env
# Отредактируйте .env, добавив свои токены

# Создать базу данных PostgreSQL
createdb omnichannel

# Запустить миграции
poetry run alembic upgrade head
```

## Запуск

```bash
# Запуск API сервера
poetry run uvicorn src.api.app:app --reload

# Откройте в браузере
open http://localhost:8000
```

## Структура проекта

```
src/
├── core/           # Абстракции (интерфейсы, модели)
├── engines/        # Движки (Telegram, Emai)
├── services/       # Сервисы (бизнес-логика)
├── infrastructure/ # БД, DI контейнер, репозитории
└── api/            # FastAPI приложение
```

## Переменные окружения

См. `.env.example` для полного списка настроек.

## Тестирование

```bash
poetry run pytest
```
