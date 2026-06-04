# PP-2026 — Omnichannel Messaging Solution

Unified messaging solution for multiple channels (Telegram, Email, Slack, Discord, VK).

## Architecture
Проект построен по **Clean Architecture**:

- **Core** — доменные модели, сервисы, ошибки
- **API** — REST-роуты, схемы, DI
- **Adapters** — интерфейсы, движки, gateway, репозитории
- **App** — DI-контейнер, конфиг, точка входа