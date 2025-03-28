# GasDynamicFrac Web App

Веб-приложение для расчётов газодинамического воздействия на продуктивные пласты.

## 📦 Стек технологий

- FastAPI (backend)
- PostgreSQL + Alembic
- Vue 3 + TypeScript (frontend)
- Docker + Docker Compose

## 🚀 Запуск проекта

1. Установите зависимости:

```bash
cd backend
pip install -r requirements.txt
```

2. Настройте переменные окружения:

```bash
cp .env.example .env
```

3. Инициализируйте базу данных:

```bash
alembic upgrade head
```

4. Запустите backend:

```bash
uvicorn my_app_api.__main__:app --reload
```

5. Перейдите в папку frontend и запустите:

```bash
cd frontend
npm install
npm run dev
```

## 📁 Структура проекта

- `backend/` — серверная часть на FastAPI
- `frontend/` — клиентская часть на Vue 3
- `migrations/` — Alembic миграции
- `schemas/`, `models/`, `routes/` — логика API

## 🛠 Переменные окружения

Пример — в `.env.example`. Используйте `DATABASE_URL`, `SECRET_KEY` и др.

