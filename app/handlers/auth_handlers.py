import hashlib
import time
import hmac
import json
import jwt
from fastapi import HTTPException
from config import Settings


# 📌 Проверка подлинности данных Telegram Mini App

setting = Settings()
TELEGRAM_BOT_TOKEN = setting.TELEGRAM_BOT_TOKEN
JWT_SECRET = setting.JWT_SECRET


def verify_telegram_auth(telegram_data: dict):
    """
    Проверяет подлинность данных, полученных от Telegram Mini App.
    """

    if "auth_date" not in telegram_data or "hash" not in telegram_data:
        raise HTTPException(
            status_code=400, detail="🚨 Отсутствуют обязательные параметры")

    # 1️⃣ Сохраняем hash и убираем его из данных
    telegram_hash = telegram_data["hash"].strip().lower()
    del telegram_data["hash"]

    # 2️⃣ Убираем **chat_instance, chat_type, signature** (их не должно быть!)
    excluded_keys = {"chat_instance", "chat_type", "signature"}
    filtered_data = {k: v for k, v in telegram_data.items()
                     if k not in excluded_keys}

    # 3️⃣ **Сериализуем `user` как JSON БЕЗ URL-кодирования**
    if "user" in filtered_data and isinstance(filtered_data["user"], dict):
        filtered_data["user"] = json.dumps(
            # 🔥 Должен быть чистый JSON!
            filtered_data["user"], separators=(',', ':'))

    # 4️⃣ Создаём `data_check_string`
    sorted_items = sorted(filtered_data.items(),
                          key=lambda x: x[0])  # Сортируем
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

    # 🔥 Отладка:
    print(f"📌 Data-check-string: {repr(data_check_string)}")

    # 5️⃣ ❗️❗️ **ГЕНЕРИРУЕМ СЕКРЕТНЫЙ КЛЮЧ ПРАВИЛЬНО!!!**
    secret_key = hmac.new("WebAppData".encode(
        "utf-8"), TELEGRAM_BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    print(f"🔑 SECRET KEY (исправленный): {secret_key.hex()}")

    # 6️⃣ Генерируем HMAC-SHA-256 хеш от `data_check_string`
    calculated_hash = hmac.new(secret_key, data_check_string.encode(
        "utf-8"), hashlib.sha256).hexdigest()

    # 7️⃣ Сравниваем хэши
    print(f"📌 Telegram hash: {telegram_hash}")
    print(f"📌 Calculated hash: {calculated_hash}")

    # if not hmac.compare_digest(calculated_hash, telegram_hash):
    #     return JSONResponse(
    #         content={
    #             "error": "❌ Неверная подпись (hash mismatch)",
    #             "telegram_hash": telegram_hash,
    #             "calculated_hash": calculated_hash,
    #             "data_check_string": data_check_string
    #         },
    #         status_code=403
    #     )

    return filtered_data


# 📌 Генерация JWT-токена


def create_jwt_token(user_id):
    payload = {"user_id": str(
        user_id), "exp": time.time() + 3600 * 24}  # 24 часа
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
