# Marketplace API

REST API для маркетплейса с аутентификацией, управлением товарами, категориями и заказами.

![Tests](https://github.com/eloquncey-collab/marketplace-api/actions/workflows/tests.yml/badge.svg)

## Стек технологий

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **JWT** — аутентификация (access tokens)
- **Docker** — контейнеризация
- **Pytest** — тестирование

## Функциональность

- Регистрация и аутентификация пользователей (JWT)
- CRUD операции для категорий, товаров, заказов
- Разграничение прав доступа (admin/user)
- Управление остатками товаров при создании заказов
- Пагинация, фильтрация, сортировка товаров

## Быстрый старт

### Через Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/eloquncey-collab/marketplace-api.git
cd marketplace-api

# Запустить проект
docker compose up --build

# API доступен на http://localhost:8000
# Документация: http://localhost:8000/docs
Локальный запуск
Требования:

Python 3.10+
PostgreSQL 15
Установка:

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env (DATABASE_URL, SECRET_KEY)

# Запустить PostgreSQL (через Docker)
docker compose up -d postgres

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn main:app --reload
Тестирование
# Запустить все тесты
pytest -q

# С покрытием
pytest --cov=app


Структура проекта
marketplace/
├── app/
│   ├── routers/       # API эндпоинты
│   ├── models.py      # SQLAlchemy модели
│   ├── schemas.py     # Pydantic схемы
│   ├── database.py    # Подключение к БД
│   ├── auth.py        # JWT логика
│   └── dependencies.py # FastAPI dependencies
├── tests/             # Pytest тесты
├── alembic/           # Миграции БД
├── Dockerfile
├── docker-compose.yml
└── requirements.txt



API Endpoints
Auth
POST /auth/register — регистрация
POST /auth/login — вход (получение токена)
Users
GET /users/me — текущий пользователь
Categories (admin only)
POST /categories/ — создать категорию
GET /categories/ — список категорий
GET /categories/{id} — получить категорию
PUT /categories/{id} — обновить категорию
DELETE /categories/{id} — удалить категорию
Products
POST /products/ — создать товар (admin)
GET /products/ — список товаров (с фильтрами)
GET /products/{id} — получить товар
PUT /products/{id} — обновить товар (admin)
DELETE /products/{id} — удалить товар (admin)
Orders
POST /orders/ — создать заказ
GET /orders/{id} — получить заказ (только свой)



Переменные окружения
DATABASE_URL=postgresql://user:password@localhost:5433/marketplace
DATABASE_URL_TEST=postgresql://user:password@localhost:5433/marketplace_test
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CI/CD
GitHub Actions автоматически запускает тесты при каждом push:

Поднимает PostgreSQL
Применяет миграции
Прогоняет pytest
Лицензия
MIT