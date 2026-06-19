# Карточка клиента (Client Profile)

## Описание

Автоматическое создание и поддержание единой карточки клиента при получении сообщений из любых каналов связи. Профиль создаётся при первом сообщении от пользователя; последующие обращения через тот же или другой канал привязываются к существующему профилю.

## Поля профиля

| Поле             | Тип               | Описание                            |
|------------------|-------------------|-------------------------------------|
| id               | str               | Уникальный идентификатор            |
| name             | str               | ФИО (заполняется из первого канала) |
| phone            | str \| null       | Номер телефона (заполняется вручную)|
| email            | str \| null       | Email (заполняется вручную)         |
| avatar_url       | str \| null       | Ссылка на аватарку пользователя     |
| channels         | ChannelIdentity[] | Список привязанных каналов связи    |
| metadata         | dict              | Дополнительные данные               |
| created_at       | datetime          | Дата создания профиля               |
| last_interaction | datetime \| null  | Дата последнего взаимодействия      |

### ChannelIdentity

| Поле         | Тип          | Описание                              |
|--------------|--------------|---------------------------------------|
| channel      | str          | Тип канала (telegram, email, и т.д.)  |
| external_id  | str          | Идентификатор пользователя в канале   |
| username     | str \| null  | Никнейм пользователя                  |
| display_name | str \| null  | Отображаемое имя                      |

## Архитектура

```
┌─────────────────────┐      ┌──────────────────────┐
│   PollingOrchestrator│──────│   ClientService       │
│   (core/services/)   │      │   (core/services/)    │
└─────────┬───────────┘      └──────────┬────────────┘
          │                            │
          │                     ┌──────┴──────┐
          │                     │ ClientRepo  │ (port)
          │                     └──────┬──────┘
          │                            │
          │                     ┌──────┴────────────┐
          │                     │ PostgresClientRepo │ (adapter)
          │                     └───────────────────┘
          │
    ┌─────┴──────┐
    │ MessageEngine│
    │ (Telegram/  │
    │  Email)     │
    └────────────┘
```

### Слой ядра (`core/`)

- **`domain/models/client.py`** — доменные сущности `Client` и `ChannelIdentity`
- **`ports/client_repository.py`** — абстрактный порт репозитория
- **`services/client_service.py`** — use case: создание, поиск, обновление, привязка каналов
- **`services/polling_service.py`** — вызов `ClientService.get_or_create_client()` при получении каждого нового сообщения

### Слой адаптеров (`adapters/`)

- **`repositories/postgres/client_models.py`** — SQLAlchemy модели `ClientModel`, `ClientChannelModel`
- **`repositories/postgres/client_repository.py`** — реализация репозитория через PostgreSQL
- **`repositories/.../repository.py`** — в `save_message` теперь также создаётся профиль клиента (через `PollingOrchestrator`)

### API слой (`api/`)

- **`routers/client_routes.py`** — эндпоинты:
  - `GET /api/clients/` — список всех клиентов
  - `GET /api/clients/{id}` — получение по ID
  - `PUT /api/clients/{id}` — ручное редактирование
  - `GET /api/clients/by-channel?channel=...&external_id=...` — поиск по каналу

### Фронтенд (`frontend/`)

- **`src/types.ts`** — TypeScript интерфейсы `Client`, `ChannelIdentity`, `ClientUpdatePayload`
- **`src/api.ts`** — функции `fetchClientByChannel`, `fetchClient`, `updateClient`
- **`src/components/ClientCard.tsx`** — React компонент карточки клиента (просмотр/редактирование)
- **`src/App.tsx`** — кнопка "Профиль" в фильтре, панель карточки над списком сообщений

## База данных

### Миграция: `alembic/versions/004_add_clients.py`

Создаёт таблицы:
- `clients` — основная информация о клиенте
- `client_channels` — привязка каналов к клиенту (внешний ключ на `clients.id`)

Индексы:
- `ix_client_channels_client_id` — поиск каналов по клиенту
- `ix_client_channels_channel_external_id` — быстрый поиск клиента по каналу

## Интеграция с каналами

При получении нового сообщения через Telegram или Email:

1. `PollingOrchestrator._poll_engine()` получает сообщение из движка
2. Вызывается `_extract_client_info()` — извлекает channel, external_id, name, username
3. `ClientService.get_or_create_client()` — ищет клиента по (channel, external_id)
4. Если найден — обновляет имя/аватар и привязывает новый канал (если ещё не привязан)
5. Если не найден — создаёт нового клиента
6. Сообщение сохраняется

## Использование

### Просмотр карточки

1. Выберите сообщение в списке (кроме сообщений агента)
2. Нажмите кнопку "Профиль" в панели фильтров
3. Карточка клиента отобразится над списком сообщений

### Редактирование

1. Откройте карточку клиента
2. Нажмите "Редактировать"
3. Измените ФИО, телефон, email
4. Нажмите "Сохранить"

## API

### `GET /api/clients/{id}`

```json
{
  "id": "client:abc123",
  "name": "Иван Иванов",
  "phone": "+79001234567",
  "email": null,
  "avatar_url": "https://...",
  "channels": [
    {
      "channel": "telegram",
      "external_id": "123456789",
      "username": "ivanov",
      "display_name": "Иван Иванов"
    }
  ],
  "metadata": {},
  "created_at": "2026-06-19T12:00:00+00:00",
  "last_interaction": "2026-06-19T14:30:00+00:00"
}
```

### `PUT /api/clients/{id}`

```json
{
  "name": "Новое Имя",
  "phone": "+79009999999",
  "email": "new@email.com"
}
```

### `GET /api/clients/by-channel?channel=telegram&external_id=123456789`

Возвращает `ClientResponse` или `null`.
