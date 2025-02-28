from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from app.logger import setup_logger
from app.routes import register_routes
from app.config import Settings


def create_app() -> FastAPI:
    app = FastAPI()

# Подключение static и templates

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
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
