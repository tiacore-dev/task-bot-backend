import hashlib
import hmac
import time
import jwt
from fastapi import HTTPException
from app.config import Settings


# 📌 Проверка подлинности данных Telegram Mini App

setting = Settings()
TELEGRAM_BOT_TOKEN = setting.TELEGRAM_BOT_TOKEN
JWT_SECRET = setting.JWT_SECRET


def verify_telegram_auth(telegram_data: dict):
    """
    Проверяем, что данные пришли действительно от Telegram.
    """
    auth_date = int(telegram_data["auth_date"])
    current_time = int(time.time())

    if current_time - auth_date > 86400:  # Данные старше 24 часов
        raise HTTPException(
            status_code=403, detail="Authentication data expired")

    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    sorted_data = "\n".join(f"{k}={v}" for k, v in sorted(
        telegram_data.items()) if k != "hash")
    data_hash = hmac.new(secret_key, sorted_data.encode(),
                         hashlib.sha256).hexdigest()

    if data_hash != telegram_data["hash"]:
        raise HTTPException(
            status_code=403, detail="Invalid authentication data")

    return telegram_data  # Данные прошли проверку


# 📌 Генерация JWT-токена
def create_jwt_token(user_id):
    payload = {"user_id": str(
        user_id), "exp": time.time() + 3600 * 24}  # 24 часа
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
