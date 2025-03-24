from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from tortoise.contrib.fastapi import register_tortoise
from logger import setup_logger
from app.routes import register_routes
from config import Settings


def create_app() -> FastAPI:
    app = FastAPI(title="Task App Backend", redirect_slashes=False)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(GZipMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Разрешает запросы отовсюду
        allow_credentials=True,
        # Разрешает все методы (GET, POST, OPTIONS и т.д.)
        allow_methods=["*"],
        # Разрешает все заголовки, включая `ngrok-skip-browser-warning`
        allow_headers=["*"],
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
