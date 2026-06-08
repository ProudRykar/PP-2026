# Roadmap — Omnichannel Messaging Solution

> Фазы развития проекта PP-2026

---

## Фаза 1: Фундамент (MVP) ✅

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Архитектура Hexagonal + Abstract Factory | ✅ | Порты/адаптеры, фабрика движков |
| DI-контейнер (punq) | ✅ | Внедрение зависимостей |
| PostgreSQL (SQLAlchemy + Alembic) | ✅ | Модели, миграции, репозиторий |
| Telegram Engine | ✅ | Чтение/отправка через бота |
| Email Engine (IMAP) | ✅ | Чтение/отправка через IMAP/SMTP |
| Litestar REST API + WebSocket | ✅ | Основные роуты, health-check |
| Frontend (React + Vite + Tailwind) | ✅ | Список сообщений, фильтр, ответ |
| S3 Gateway | ✅ | Хранение вложений |
| MkDocs | ✅ | Документация кода |

```mermaid
gantt
    title Фаза 1: Фундамент (MVP)
    dateFormat  YYYY-MM-DD
    axisFormat  %Y-%m

    section Архитектура
    Hexagonal + DI         :done, arch1, 2025-01-01, 2025-02-15
    Порты и интерфейсы     :done, arch2, 2025-02-01, 2025-03-01

    section Хранение
    PostgreSQL модели      :done, db1, 2025-02-01, 2025-03-01
    Репозиторий + миграции :done, db2, 2025-03-01, 2025-04-01

    section Движки
    Telegram Engine         :done, eng1, 2025-03-01, 2025-04-15
    Email Engine (IMAP)     :done, eng2, 2025-04-01, 2025-05-15
    S3 Gateway              :done, eng3, 2025-04-15, 2025-05-15

    section API & Frontend
    Litestar REST + WS      :done, api1, 2025-04-01, 2025-05-15
    React Frontend          :done, fe1, 2025-05-01, 2025-06-01

    section Docs
    MkDocs + gutarik        :done, docs1, 2025-05-15, 2025-06-01
```

---

## Фаза 2: Расширение каналов 🚧

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Slack Engine | 🚧 Планируется | Интеграция через Slack Bolt |
| Discord Engine | 🚧 Планируется | Интеграция через discord-py |
| WhatsApp / SMS | 📋 Идея | Twilio / провайдеры |
| Умное распределение (Routing) | 📋 Идея | automatic channel routing |
| Шаблоны ответов | 📋 Идея | Canned responses |
| Attachments UI | 🚧 В планах | Просмотр вложений в фронтенде |
| Push-уведомления | 📋 Идея | Web Push / Email |

```mermaid
gantt
    title Фаза 2: Расширение каналов
    dateFormat  YYYY-MM-DD
    axisFormat  %Y-%m

    section Новые каналы
    Slack Engine            :active, s1, 2025-06-01, 2025-07-15
    Discord Engine          :       s2, 2025-07-01, 2025-08-15

    section Фронтенд
    Вложения UI             :active, f1, 2025-06-15, 2025-07-15
    Умный поиск             :       f2, 2025-07-15, 2025-08-15

    section Инфраструктура
    CI/CD (GitHub Actions)  :active, ci1, 2025-06-01, 2025-07-01
    Мониторинг + логи       :       ci2, 2025-07-01, 2025-08-01
```

---

## Фаза 3: Production Ready

```mermaid
flowchart LR
    subgraph Phase3[Фаза 3: Production]
        A[Нагрузочное тестирование] --> B[Оптимизация]
        B --> C[Kubernetes deployment]
        C --> D[Rate limiting + Auth]
        D --> E[SLA мониторинг]
    end

    style Phase3 fill:#e1f5fe,stroke:#01579b
```

| Компонент | Приоритет | Описание |
|-----------|-----------|----------|
| Auth / RBAC | Высокий | JWT, роли пользователей |
| Rate limiting | Высокий | Защита API |
| Нагрузочное тестирование | Средний | k6 / locust |
| Kubernetes | Средний | helm-чарты, автоскейлинг |
| Sentry / Grafana | Средний | Мониторинг ошибок и метрик |
| Internationalization | Низкий | i18n для UI |

---

## Архитектура проекта (текущая)

```mermaid
graph TB
    subgraph Frontend["Frontend (React + Vite)"]
        UI[React UI]
        WS[WebSocket Client]
    end

    subgraph API["API Layer (Litestar)"]
        REST[REST Endpoints]
        WSS[WebSocket Handler]
        DEP[DI Dependencies]
    end

    subgraph Core["Core (Business Logic)"]
        MS[Message Service]
        PS[Polling Service]
        PORTS[Ports / Interfaces]
        MODELS[Domain Models]
    end

    subgraph Engines["Engines (Channels)"]
        TF[Telegram Factory]
        EF[Email Factory]
        SF[Slack Factory<br/>🔄 planned]
        DF[Discord Factory<br/>🔄 planned]
        AF[Abstract Engine Factory]
    end

    subgraph Storage["Storage"]
        PG[(PostgreSQL)]
        S3[(S3 / MinIO)]
        REPO[Repositories]
    end

    Frontend -->|HTTP / WS| API
    API --> Core
    Core --> Engines
    Core --> Storage
    Engines -->|Polling| Core
```

---

## Dependency Graph

```mermaid
graph LR
    punq[punq DI] --> Container[Container]
    Container --> API[API Router]
    Container --> MS[Message Service]
    Container --> PS[Polling Service]
    Container --> AF[Engine Factory]
    AF --> TE[Telegram Engine]
    AF --> EE[Email Engine]
    AF --> SE[Slack Engine 🚧]
    AF --> DE[Discord Engine 🚧]
    MS --> MR[Message Repository]
    MR --> PG[PostgreSQL]
    MS --> S3G[S3 Gateway]
    S3G --> S3B[(S3)]
```

---

## Легенда

- ✅ — Реализовано
- 🚧 — В процессе / планируется
- 📋 — В бэклоге
