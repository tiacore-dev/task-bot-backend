import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "default_connection": "default",  # <-- Добавь сюда
}
