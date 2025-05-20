# Foodgram - веб-сервис для обмена рецептами

<https://foodgram.serveirc.com>

Веб-приложение, где пользователи могут делиться рецептами, подписываться на авторов, сохранять рецепты в избранное и формировать список покупок. Проект реализован с чистой архитектурой и развёрнут в Docker-контейнерах.

<img src="foodgram.png" width="800" height: auto>

## Стек технологий

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

## Основные функции

- Регистрация и аутентификация пользователей
- Публикация рецептов с возможностью добавления изображений
- Добавление рецептов в избранное
- Подписка на других пользователей
- Формирование списка покупок
- Поиск рецептов по тегам и ингредиентам

## Установка

### Клонирование репозитория

```bash
git clone https://github.com/Filichkin/foodgram.git
cd foodgram
```

## Структура проекта

- `backend/` — содержит исходный код серверной части приложения.
- `foodgram/` — основное приложение Django.
- `recipes/` — приложение для работы с рецептами.
- `users/` — приложение для управления пользователями.
- `api/` — реализация API на основе Django REST Framework.
- `frontend/` — исходный код клиентской части (если есть).
- `api/docs/` — документация по проекту.

## API документация

Проект включает API для взаимодействия с фронтендом и другими приложениями. Основные эндпоинты:

- `GET /api/recipes/` — получение списка рецептов.
- `POST /api/recipes/` — создание нового рецепта.
- `GET /api/ingredients/` — поиск ингредиентов по названию.
- `POST /api/users/` — регистрация нового пользователя.

Более подробные требования к полям моделей можно найти в спецификации к API.
Находясь в папке infra, выполните в терминале команду:
```docker compose up```

По адресу <http://localhost> изучите фронтенд веб-приложения, а по адресу <http://localhost/api/docs/> — спецификацию API.


## Развёртывание

Для развертывания проекта используйте Docker. Убедитесь, что у вас установлены Docker и Docker Compose. Выполните следующие команды:
```
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose exec backend python manage.py csv_upload
```
После успешного выполнения этих команд приложение будет доступно по адресу <http://localhost:8000>.

## Настройки окружения

Перед запуском приложения настройте переменные окружения (пример в файле .env_example):

- `POSTGRES_USER`— пользователь базы данных.
- `POSTGRES_PASSWORD`— пароль пользователя базы данных.
- `POSTGRES_DB`— имя базы данных PostgreSQL.
- `SECRET_KEY` — секретный ключ Django.
- `DB_HOST` — хост базы данных.
- `DB_PORT` — порт для подключения к базе данных.
- `ALLOWED_HOSTS` — список доступных хостов.
- `DEBUG` — статус отладки Django.
- `CSRF_TRUSTED_ORIGINS` — список доменов от которых Django будет доверять incoming requests с CSRF-токенами.






