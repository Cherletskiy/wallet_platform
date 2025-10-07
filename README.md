# Wallet API

## Описание проекта

Wallet API — это REST API для управления балансом кошельков, реализованное на FastAPI с использованием PostgreSQL. Поддерживает операции пополнения (DEPOSIT) и снятия (WITHDRAWAL) средств, с учётом конкурентного доступа через `SELECT FOR UPDATE`. Все денежные суммы хранятся в копейках (центах) для точности, но API принимает и возвращает суммы в рублях. Проект включает тесты pytest (94% покрытия), логирование, миграции через Alembic и контейнеризацию с Docker.

## Требования

- Python 3.12+
- Docker и Docker Compose
- PostgreSQL 15+
- Зависимости из `requirements.txt`:
  - `fastapi==0.118.0`
  - `uvicorn==0.37.0`
  - `pydantic==2.11.9`
  - `SQLAlchemy[asyncio]==2.0.43`
  - `asyncpg==0.30.0`
  - `alembic==1.16.5`
  - `psycopg2-binary==2.9.10`
  - `python-dotenv==1.1.1`
  - `pytest>=7.0.0`
  - `pytest-asyncio>=0.21.0`
  - `pytest-cov>=4.0.0`
  - `httpx>=0.24.0`

## Структура проекта

```
FastAPI_Wallet/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # Эндпоинты API
│   │   │   ├── schemas.py       # Pydantic-схемы
│   │   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Настройки окружения
│   │   ├── database.py          # Инициализация БД
│   │   ├── dependencies.py      # Зависимости FastAPI
│   │   ├── logging_config.py    # Настройка логирования
│   │   ├── migrations.py        # Запуск миграций Alembic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── wallet.py            # SQLAlchemy-модели (Wallet, Operation)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── wallet_repository.py # Логика работы с БД
│   ├── services/
│   │   ├── __init__.py
│   │   ├── wallet_service.py    # Бизнес-логика
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Фикстуры для тестов
│   │   ├── test_concurrency.py  # Тесты конкурентности
│   │   ├── test_repository.py   # Тесты репозитория
│   │   ├── test_routes.py       # Тесты эндпоинтов
│   │   ├── test_services.py     # Тесты сервиса
├── alembic/
│   ├── versions/                # Файлы миграций
│   ├── env.py                  # Настройка Alembic
├── .coveragerc                 # Настройка pytest-cov
├── .env                        # Переменные окружения
├── alembic.ini                 # Конфигурация Alembic
├── docker-compose.yml          # Docker Compose для приложения, БД и pgAdmin
├── Dockerfile                  # Docker для приложения
├── pytest.ini                  # Настройка pytest
├── requirements.txt            # Зависимости
└── README.md
```

## Установка и запуск

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository-url>
   cd FastAPI_Wallet
   ```

2. **Настройте переменные окружения**:
   - Скопируйте `_env` в `.env` и укажите значения:
     ```env
     DB_NAME=postgres
     DB_USER=postgres
     DB_PWD=postgres
     DB_HOST=db
     DB_PORT=5432
     TEST_DB_NAME=test_wallet_db
     TEST_DB_USER=postgres
     TEST_DB_PWD=postgres
     TEST_DB_HOST=test_db
     TEST_DB_PORT=5432
     PGADMIN_DEFAULT_EMAIL=admin@admin.com
     PGADMIN_DEFAULT_PASSWORD=admin
     ```

3. **Запустите Docker Compose**:
   ```bash
   docker-compose up -d
   ```
   - Запустит:
     - Основную БД (`db`, port 5431)
     - Тестовую БД (`test_db`, port 5433)
     - pgAdmin (`pgadmin`, port 8080)
     - Приложение FastAPI (`app`, port 8000)

4. **Создайте кошелёк**:
   - API не предусматривает создание кошельков (по ТЗ). Создайте кошелёк вручную:
     - Через **pgAdmin** (http://localhost:8080, логин: `admin@admin.com`, пароль: `admin`):
       - Подключитесь к БД (`db`, host: `db`, port: 5432, user: `postgres`, password: `postgres`).
       - Выполните SQL: `INSERT INTO wallets (id, balance_cent) VALUES (gen_random_uuid(), 0);`.
     - Или через `psql`:
       ```bash
       docker-compose exec db psql -U postgres -d postgres
       INSERT INTO wallets (id, balance_cent) VALUES (gen_random_uuid(), 0);
       ```

5. **Проверьте API**:
   - Swagger UI: http://localhost:8000/docs
   - Проверьте эндпоинты (см. ниже).

## Эндпоинты API

- **GET /api/v1/wallets/{wallet_id}**:
  - Возвращает баланс кошелька в рублях.
  - Параметры: `wallet_id` (UUID).
  - Ответ: `{"balance_rub": float}` (например, `{"balance_rub": 100.50}`).
  - Ошибки: 404 (кошелёк не найден), 422 (некорректный UUID).

- **POST /api/v1/wallets/{wallet_id}/operation**:
  - Выполняет операцию DEPOSIT или WITHDRAWAL.
  - Параметры: `wallet_id` (UUID).
  - Тело запроса:
    ```json
    {
      "amount": float,
      "operation_type": "DEPOSIT" | "WITHDRAWAL"
    }
    ```
  - Ответ: `{"balance_rub": float}` (новый баланс).
  - Ошибки: 400 (недостаточно средств, amount <= 0), 404 (кошелёк не найден), 422 (некорректные данные).

## База данных

- **Основная БД**: PostgreSQL (host: `db`, port: 5431:5432, имя: `postgres`).
- **Тестовая БД**: PostgreSQL (host: `test_db`, port: 5433:5432, имя: `test_wallet_db`).
- **Таблицы**:
  - `wallets`: Кошельки (`id: UUID`, `balance_cent: int`, `created_at: timestamp`).
    - Ограничение: `balance_cent >= 0`.
  - `operations`: Операции (`id: int`, `wallet_id: UUID`, `operation_type: ENUM("DEPOSIT", "WITHDRAWAL")`, `amount_cent: int`, `created_at: timestamp`).
- **Миграции**: Управляются через Alembic для основной БД (папка `alembic/`).

## Тесты

- **Покрытие**: 94%.
  ```
  Name                                    Stmts   Miss  Cover
  -----------------------------------------------------------
  app/__init__.py                             0      0   100%
  app/api/__init__.py                         0      0   100%
  app/api/v1/__init__.py                      0      0   100%
  app/api/v1/routes.py                       15      0   100%
  app/api/v1/schemas.py                       8      0   100%
  app/core/__init__.py                        0      0   100%
  app/core/config.py                         11      0   100%
  app/core/database.py                       18      4    78%
  app/core/dependencies.py                   22      1    95%
  app/core/logging_config.py                 14      0   100%
  app/core/migrations.py                     13      0   100%
  app/main.py                                20      2    90%
  app/models/__init__.py                      0      0   100%
  app/models/wallet.py                       26      0   100%
  app/repositories/__init__.py                0      0   100%
  app/repositories/wallet_repository.py      19      0   100%
  app/services/__init__.py                    0      0   100%
  app/services/wallet_service.py             42      5    88%
  -----------------------------------------------------------
  TOTAL                                     208     12    94%
  ```
- **Файлы тестов**:
  - `test_routes.py`: Тесты эндпоинтов (успех, ошибки 400/404/422).
  - `test_services.py`: Юнит-тесты сервиса (WalletService).
  - `test_repository.py`: Тесты репозитория (WalletRepository).
  - `test_concurrency.py`: Тесты конкурентности (25 deposit + 25 withdrawal с `SELECT FOR UPDATE`).
- **Запуск тестов**:
  ```bash
  docker-compose exec app pytest app/tests -v --cov=app --cov-report=term
  ```
- Тесты используют изолированную БД (`test_db`, port 5433) с `Base.metadata.create_all`.

## Логирование

- Логи пишутся в `app.log` с ротацией (10 МБ, 5 файлов).
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
- Логируются успешные операции, ошибки и события жизненного цикла приложения.

## pgAdmin

- Доступ: http://localhost:8080
- Логин: `admin@admin.com`, пароль: `admin`.
- Используйте для просмотра/управления основной (`db`) и тестовой (`test_db`) БД.
- Подключение:
  - Основная БД: host=`db`, port=5432, user=`postgres`, password=`postgres`.
  - Тестовая БД: host=`test_db`, port=5432, user=`postgres`, password=`postgres`.

## Дополнительные замечания

- **Конкурентность**: Реализована через `SELECT FOR UPDATE` в `WalletRepository.get_wallet_by_id`.
- **Точность**: Баланс хранится в копейках (`balance_cent`), API работает с рублями (`Decimal | float`).
- **Создание кошельков**: Не предусмотрено API, используйте pgAdmin или `psql` для создания кошельков.
- **CI/CD**: Не настроен, тесты запускаются вручную.
