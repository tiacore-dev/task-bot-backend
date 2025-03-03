import hashlib
import time
import unicodedata
import hmac
from collections import OrderedDict
import jwt
from fastapi import HTTPException
from app.config import Settings


# 📌 Проверка подлинности данных Telegram Mini App

setting = Settings()
TELEGRAM_BOT_TOKEN = setting.TELEGRAM_BOT_TOKEN
JWT_SECRET = setting.JWT_SECRET


def verify_telegram_auth(telegram_data: dict):
    """
    Проверяет подлинность данных, полученных от Telegram.
    """

    if "auth_date" not in telegram_data or "hash" not in telegram_data:
        raise HTTPException(
            status_code=400, detail="🚨 Отсутствуют обязательные параметры")

    # 1️⃣ Проверяем срок действия данных (не старше 24 часов)
    auth_date = int(telegram_data["auth_date"])
    current_time = int(time.time())

    if current_time - auth_date > 86400:
        raise HTTPException(status_code=403, detail="⏳ Данные устарели")

    # 🚨 2️⃣ **Используем правильный секретный ключ (Telegram требует WebAppData!)**
    secret_key = hmac.new(TELEGRAM_BOT_TOKEN.encode(
        "utf-8"), b"WebAppData", hashlib.sha256).digest()
    print(
        f"🔑 Секретный ключ (SHA256 от WebAppData + токен): {secret_key.hex()}")

    # 3️⃣ Фильтруем входные данные (убираем `hash`, `signature`, пустые значения)
    filtered_data = {}
    for k, v in telegram_data.items():
        if k in ["hash", "signature"]:
            continue  # Исключаем эти поля
        if isinstance(v, dict):  # Обрабатываем вложенные объекты **БЕЗ `user.`**
            for sub_k, sub_v in v.items():
                if sub_v in [None, ""]:  # Исключаем пустые строки
                    continue
                if isinstance(sub_v, bool):  # True/False -> "1"/"0"
                    sub_v = "1" if sub_v else "0"
                filtered_data[sub_k] = unicodedata.normalize(
                    "NFKC", str(sub_v))  # Убираем `user.`
        else:
            if v in [None, ""]:  # Исключаем пустые строки
                continue
            if isinstance(v, bool):  # True/False -> "1"/"0"
                v = "1" if v else "0"
            filtered_data[k] = unicodedata.normalize("NFKC", str(v))

    # 4️⃣ **Создаём OrderedDict с фиксированным порядком Telegram**
    ordered_keys = [
        "auth_date", "chat_instance", "chat_type",
        "allows_write_to_pm", "first_name",
        "id", "is_premium", "language_code",
        "photo_url", "username"
    ]

    ordered_data = OrderedDict()
    for key in ordered_keys:
        if key in filtered_data:
            ordered_data[key] = filtered_data[key]

    # 5️⃣ **Формируем строку строго по правилам Telegram**
    check_string = "\n".join(f"{k}={v}" for k, v in ordered_data.items())

    print(f"📌 Итоговая строка проверки данных:\n{check_string}\n")

    # 6️⃣ **Вычисляем HMAC-SHA256 с правильным ключом**
    calculated_hash = hmac.new(secret_key, check_string.encode(
        "utf-8"), hashlib.sha256).hexdigest()

    # 7️⃣ Telegram передает `hash` в HEX — приводим к нижнему регистру
    telegram_hash = telegram_data["hash"].lower()

    print(f"📌 Telegram передал hash: {telegram_hash}")
    print(f"📌 Вычисленный hash: {calculated_hash}")

    # 8️⃣ Сравниваем `hash`
    if not hmac.compare_digest(calculated_hash, telegram_hash):
        raise HTTPException(
            status_code=403, detail="❌ Неверная подпись (hash mismatch)")

    return telegram_data  # ✅ Данные валидны
# 📌 Генерация JWT-токена


def create_jwt_token(user_id):
    payload = {"user_id": str(
        user_id), "exp": time.time() + 3600 * 24}  # 24 часа
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
