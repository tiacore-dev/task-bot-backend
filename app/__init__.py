from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from logger import setup_logger
from app.routes import register_routes
from config import Settings


def create_app() -> FastAPI:
    app = FastAPI(title="Task App Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Или указать твой Netlify-домен
        allow_credentials=True,
        # Разрешаем все методы (POST, GET, OPTIONS и т.д.)
        allow_methods=["*"],
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    app.state.settings = Settings()
   # Конфигурация Tortoise ORM
    register_tortoise(
        app,
        db_url=Settings.DATABASE_URL,
        modules={"models": ["app.database.models"]},
        # generate_schemas=True,
        add_exception_handlers=True,
    )

    setup_logger()
    # Регистрация маршрутов
    register_routes(app)

    return app
