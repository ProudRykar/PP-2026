# Omnichannel Messaging Solution

Единое окно для просмотра и ответа на сообщения из Telegram, Email и других каналов.

## Быстрый старт (Docker Compose)

**Требования:** Docker, Docker Compose, git.

```bash
git clone <репозиторий> omnichannel
cd omnichannel

# Скопировать настройки
cp .env.example .env
```

Отредактируйте `.env` — минимум нужно указать:

- `TELEGRAM_BOT_TOKEN` — токен бота (как получить — ниже)
- `EMAIL_PASSWORD` — пароль приложения для почты (как получить — ниже)
- `JWT_SECRET` — любой сложный пароль (или оставьте `change-me`)

Запустить:

```bash
docker compose up --build
```

Всё соберётся и запустится. Откройте **http://localhost:8000** в браузере.

**Что поднимается:**
| Сервис | Порт | Описание |
|--------|------|----------|
| Приложение | `8000` | Фронтенд + API |
| PostgreSQL | `5432` | База данных |
| MinIO | `9000` / `9001` | S3-хранилище (файлы) |

При первом запуске миграции БД накатываются автоматически.

---

## Детальный запуск (без Docker)

### 1. База данных

```bash
# Установите PostgreSQL, затем:
createdb omnichannel
```

### 2. Бэкенд

```bash
# Установите Python 3.14+ и Poetry
poetry install
cp .env.example .env
# Отредактируйте .env под себя

# Применить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Фронтенд

```bash
cd frontend
npm install
npm run build    # сборка для продакшена
# или
npm run dev      # режим разработки (порт 5173 с прокси на 8000)
```

В продакшене фронтенд раздаётся самим бэкендом на порту `8000`. В режиме `dev` используйте Vite на порту `5173` — он будет проксировать API-запросы на бэкенд.

---

## Настройка каналов

### Telegram

1. Найдите в Telegram бота [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Введите **имя** бота (отображаемое, любое)
4. Введите **username** бота (должен заканчиваться на `bot`, например `MySupportBot`)
5. BotFather выдаст токен — скопируйте его
6. Вставьте токен в `.env`:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrstUVwxyz
```

### Email (на примере Yandex)

1. Зайдите в почтовый ящик на yandex.ru
2. Нажмите на значок шестерёнки → **«Все настройки»**
3. Перейдите в раздел **«Почтовые программы»**
4. Поставьте галочку **«С сервера imap.yandex.ru по протоколу IMAP»**
5. Перейдите в раздел **«Безопасность»**
6. В абзаце про пароли приложений нажмите ссылку **«Создайте и включите пароли приложений»**
7. В выпадающем списке выберите **«Почта»** и нажмите «Создать»
8. Яндекс покажет ключ (16 символов) — **скопируйте и сохраните** (он показывается один раз)
9. Укажите ваши данные в `.env`:

```
EMAIL_HOST=imap.yandex.ru
EMAIL_PORT=993
EMAIL_USER=ваш_логин@yandex.ru
EMAIL_PASSWORD=сгенерированный_ключ
EMAIL_POLL_INTERVAL=60
EMAIL_SMTP_HOST=smtp.yandex.ru
EMAIL_SMTP_PORT=465
```
---

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `DATABASE_USER` | `user` | Пользователь PostgreSQL |
| `DATABASE_PASSWORD` | `password` | Пароль PostgreSQL |
| `DATABASE_HOST` | `localhost` | Хост PostgreSQL |
| `DATABASE_PORT` | `5432` | Порт PostgreSQL |
| `DATABASE_NAME` | `omnichannel` | Имя БД |
| `DATABASE_URL` | — | Полный URL (перекрывает остальные настройки БД) |
| `MINIO_ENDPOINT` | `http://localhost:9000` | Адрес MinIO |
| `MINIO_ACCESS_KEY` | `minioadmin` | Ключ доступа MinIO |
| `MINIO_SECRET_KEY` | `minioadmin` | Секретный ключ MinIO |
| `MINIO_BUCKET` | — | Имя корзины MinIO |
| `TELEGRAM_BOT_TOKEN` | — | Токен Telegram-бота |
| `EMAIL_HOST` | — | IMAP-сервер (например `imap.yandex.ru`) |
| `EMAIL_PORT` | `993` | Порт IMAP |
| `EMAIL_USER` | — | Логин email |
| `EMAIL_PASSWORD` | — | Пароль приложения (не основной!) |
| `EMAIL_SMTP_HOST` | как `EMAIL_HOST` | SMTP-сервер для отправки |
| `EMAIL_SMTP_PORT` | `587` | Порт SMTP |
| `EMAIL_POLL_INTERVAL` | `60` | Интервал проверки почты (сек) |
| `JWT_SECRET` | `change-me` | Секрет для JWT-токенов |
| `JWT_ALGORITHM` | `HS256` | Алгоритм JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Время жизни токена |
| `DEBUG` | `false` | Режим отладки |
| `LOG_LEVEL` | `INFO` | Уровень логов |

---

## Архитектура

```
клиент (браузер) → HTTP / WS → бэкенд (Litestar) → PostgreSQL
                                    ↓
                              Telegram Bot / IMAP / SMTP
```

- **Бэкенд**: Python 3.14+, Litestar (REST + WebSocket + статика), SQLAlchemy (async), asyncpg
- **Фронтенд**: React 19, TypeScript, Vite, Tailwind CSS
- **Движки**: Abstract Factory — каждый канал (Telegram, Email) реализует общий интерфейс
- **DI**: punq-контейнер с синглтон-скоупингом
- **Файлы**: MinIO (S3-совместимое хранилище)
- **Аутентификация**: JWT + bcrypt

## Структура проекта

```
├── app/
│   ├── main.py              # Точка входа бэкенда
│   ├── config.py            # Конфигурация из .env
│   ├── container.py         # DI-контейнер
│   ├── api/
│   │   └── routers/         # REST-эндпоинты
│   └── core/
│       ├── domain/models/   # Модели данных
│       ├── services/        # Бизнес-логика
│       ├── ports/           # Интерфейсы
│       └── errors/          # Ошибки
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Главный компонент
│   │   ├── api.ts           # API-клиент
│   │   ├── types.ts         # TypeScript-типы
│   │   └── components/      # React-компоненты
│   └── package.json
├── Dockerfile               # Сборка бэкенда + фронтенда
├── docker-compose.yml       # Поднять всё сразу
└── .env.example             # Шаблон настроек
```

## Тестирование

```bash
# бэкенд
poetry run pytest

# фронтенд
cd frontend && npm run build   # проверит TypeScript + сборку
```
