import json
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import User, UserAccount
from app.pydantic_models.user_schemas import UserSchema, UserCreateSchema, UserResponseSchema
from app.pydantic_models.account_schemas import UserAccountSchema
from app.handlers.auth_handlers import verify_telegram_auth

account_router = APIRouter(prefix="/account", tags=["account"])


@account_router.post("/auth", response_model=UserResponseSchema)
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


# 📌 2. Получение информации о текущем пользователе
@account_router.get("/me", response_model=UserSchema)
async def get_current_user(user: User = Depends(get_user_by_telegram_id)):
    # Конвертация Tortoise ORM в Pydantic
    return UserSchema.model_validate(user)


# 📌 3. Обновление информации о пользователе
@account_router.put("/me", response_model=UserSchema)
async def update_user(data: UserCreateSchema, user: User = Depends(get_user_by_telegram_id)):
    """
    Обновление информации о пользователе (например, имени).
    """
    user.username = data.username or user.username
    await user.save()
    return user


# 📌 4. Привязка нового аккаунта соцсети
@account_router.post("/accounts", response_model=UserAccountSchema)
async def add_account(account_data: UserAccountSchema, user: User = Depends(get_user_by_telegram_id)):
    """
    Привязка соцсети (YouTube, Twitter, Telegram и т. д.).
    """
    account = await UserAccount.create(
        user_id=user.user_id,
        platform=account_data.platform,
        account_name=account_data.account_name,
        account_platform_id=account_data.account_platform_id,
    )
    return account


# 📌 5. Получение всех привязанных соцсетей пользователя
@account_router.get("/accounts", response_model=list[UserAccountSchema])
async def get_accounts(user: User = Depends(get_user_by_telegram_id)):
    """
    Получение списка привязанных соцсетей.
    """
    return await UserAccount.filter(user_id=user.user_id).all()
