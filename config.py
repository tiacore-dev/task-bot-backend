import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES")
    # LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_LEVEL = "DEBUG"
    ALGORITHM = "HS256"
    PORT = os.getenv('PORT')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    JWT_SECRET = os.getenv('JWT_SECRET')
    ENDPOINT_URL = os.getenv('ENDPOINT_URL')
    REGION_NAME = os.getenv('REGION_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID ')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
