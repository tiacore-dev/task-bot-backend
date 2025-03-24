import json
from fastapi import APIRouter, HTTPException
from loguru import logger
from app.database.models import User
from app.pydantic_models.user_schemas import UserResponseSchema
from app.handlers.auth_handlers import verify_telegram_auth


auth_router = APIRouter(prefix="/accounts", tags=["account"])


@auth_router.post("/auth", response_model=UserResponseSchema)
async def auth(telegram_data: dict):
    """
    Аутентификация через Telegram Mini App.
    """
    logger.info("📌 Полученные данные от Telegram: %s", telegram_data)

    try:
        # 🔹 Проверяем подпись Telegram
        user_data = verify_telegram_auth(telegram_data)
        logger.info("📌 После верификации Telegram: %s", user_data)

        if not user_data:
            logger.warning("🚨 Ошибка верификации Telegram-данных!")
            raise HTTPException(
                status_code=403, detail="Invalid Telegram auth data")

        # 🔹 Декодируем `user` (он приходит как JSON-строка!)
        if isinstance(user_data["user"], str):
            user_data["user"] = json.loads(user_data["user"])

        logger.info("📌 Декодированные данные пользователя: %s",
                    user_data["user"])

        telegram_id = user_data["user"]["id"]
        username = user_data["user"]["username"]

        logger.info("📌 Telegram ID: %s | Username: %s", telegram_id, username)

        # 🔹 Проверяем, есть ли пользователь в БД
        user = await User.get_or_none(telegram_id=telegram_id)
        if user:
            logger.info("✅ Пользователь найден в БД: %s", user)
        else:
            logger.info("🆕 Пользователь НЕ найден, создаем нового...")
            user = await User.create(
                telegram_id=telegram_id,
                username=username,
                role_id="executor",  # По умолчанию – исполнитель
                balance=0,
            )
            logger.info("✅ Новый пользователь создан: %s", user)

        # 🔹 Возвращаем ID пользователя
        logger.info("📌 Возвращаем user_id: %s", user.user_id)
        return UserResponseSchema(user_id=user.user_id, username=user.username)

    except Exception as e:
        logger.exception("❌ Ошибка в auth(): %s", str(e))
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from e
