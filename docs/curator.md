# Система кураторов

## Обзор

Система кураторов позволяет создавать профили сотрудников (кураторов), назначать их ответственными за обращения (сообщения) и передавать обращения между кураторами с сохранением полной истории изменений.

## Доменная модель

### Curator (куратор)

Поля профиля:

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `str` | Уникальный идентификатор (`curator:<uuid>`) |
| `full_name` | `str` | ФИО куратора |
| `login` | `str` | Уникальный логин |
| `email` | `str` | Email |
| `role` | `CuratorRole` | Роль: `admin`, `supervisor`, `agent` |
| `status` | `CuratorStatus` | Статус: `active`, `inactive` |
| `avatar_url` | `str\|None` | Ссылка на аватар |
| `created_at` | `datetime` | Дата регистрации |
| `last_activity` | `datetime\|None` | Дата последней активности |

### AssignmentHistory (история назначений)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `str` | Уникальный идентификатор |
| `message_id` | `str` | ID обращения |
| `from_curator_id` | `str\|None` | Предыдущий куратор (`null` = не назначено) |
| `to_curator_id` | `str\|None` | Новый куратор |
| `assigned_by` | `str\|None` | Кто выполнил назначение |
| `reason` | `str\|None` | Причина передачи |
| `created_at` | `datetime` | Дата назначения |

## API Endpoints

### Управление кураторами

| Метод | Path | Описание |
|-------|------|----------|
| `POST` | `/api/curators` | Создать куратора |
| `GET` | `/api/curators` | Список кураторов (`?status=active`) |
| `GET` | `/api/curators/{id}` | Получить куратора |
| `PUT` | `/api/curators/{id}` | Обновить куратора |
| `PATCH` | `/api/curators/{id}/status` | Сменить статус |
| `DELETE` | `/api/curators/{id}` | Удалить куратора |

### Назначение и передача

| Метод | Path | Описание |
|-------|------|----------|
| `POST` | `/api/messages/{id}/assign` | Назначить куратора на обращение |
| `POST` | `/api/messages/{id}/transfer` | Передать обращение другому куратору |
| `GET` | `/api/messages/{id}/assignments` | История назначений обращения |
| `GET` | `/api/curators/{id}/assignments` | История назначений куратора |

### Фильтрация сообщений

| Метод | Path | Описание |
|-------|------|----------|
| `GET` | `/api/messages?curator_id={id}` | Сообщения закреплённые за куратором |

## WebSocket уведомления

При назначении или передаче куратора отправляется WebSocket-событие:

```json
{
  "type": "curator_assigned",
  "message_id": "msg:xxx",
  "curator_id": "curator:xxx",
  "assigned_by": "curator:xxx",
  "timestamp": "2026-06-24T12:00:00+00:00"
}
```

```json
{
  "type": "curator_transferred",
  "message_id": "msg:xxx",
  "from_curator_id": "curator:old",
  "to_curator_id": "curator:new",
  "assigned_by": "curator:admin",
  "reason": "Передача по нагрузке",
  "timestamp": "2026-06-24T12:00:00+00:00"
}
```

## Бизнес-правила

1. Обращение может иметь только **одного** ответственного куратора одновременно
2. Нельзя назначить неактивного (`inactive`) куратора
3. Нельзя повторно назначить того же куратора (будет `CuratorAlreadyAssignedError`)
4. При передаче сохраняется полная история: кто от кого кому передал
5. История включает причину передачи (`reason`)

## Архитектура

```
app/
  core/
    domain/models/
      curator.py          # Curator, AssignmentHistory dataclasses
      channel_type.py     # CuratorRole, CuratorStatus enums
      message.py          # Message (добавлен curator_id)
    ports/
      curator_repository.py  # CuratorRepository, AssignmentHistoryRepository ABC
      message_repository.py  # MessageRepository (добавлен curator_id, update_curator)
    services/
      curator_service.py     # CuratorService (бизнес-логика)
    errors/
      curator.py             # Кастомные исключения
  adapters/repositories/postgres/
    curator_models.py        # SQLAlchemy модели
    curator_repository.py    # Postgres реализация
    models.py                # MessageModel (добавлен curator_id)
  api/
    routers/
      curator_routes.py      # CuratorController, AssignmentController
      routes.py              # get_messages (добавлен curator_id filter)
    schemas/
      curator_dto.py         # CuratorResponse, CreateRequest, etc.
      message_dto.py         # MessageResponse (добавлен curator_id)
    dependencies.py          # get_curator_service()
  container.py               # Регистрация новых типов
  main.py                    # Подключение routes и dependency
```

## Миграция БД

`alembic/versions/005_add_curators.py` — создаёт таблицы `curators`, `assignment_history` и добавляет колонку `curator_id` в `messages`.

## Тесты

- `tests/test_curator_service.py` — 21 тест (создание, валидация, назначение, передача, история)
- `tests/test_container.py` — проверка разрешения новых типов в DI
- Все тесты: `pytest tests/ --ignore=tests/test_api_routes.py --ignore=tests/test_polling_service.py`
