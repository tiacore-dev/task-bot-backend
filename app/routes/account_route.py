from fastapi import APIRouter, Depends, HTTPException
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import User, UserAccount
from app.pydantic_models.user_schemas import UserSchema, UserCreateSchema
from app.pydantic_models.account_schemas import UserAccountSchema
from app.handlers.auth_handlers import verify_telegram_auth, create_jwt_token


account_router = APIRouter(prefix="/account", tags=["account"])

# 📌 1. Авторизация через Telegram Mini App


@account_router.post("/auth")
async def auth(telegram_data: dict):
    """
    Аутентификация через Telegram Mini App.
    """
    print("📌 Полученные данные от Telegram:", telegram_data)  # Логируем данные

    user_data = verify_telegram_auth(telegram_data)  # Проверяем подпись

    if not user_data:
        raise HTTPException(
            status_code=403, detail="Invalid Telegram auth data")

    telegram_id = user_data["id"]
    username = user_data.get("username")

    user = await User.get(telegram_id=telegram_id)

    if not user:
        user = await User.create(
            telegram_id=telegram_id,
            username=username,
            role_id="executor",  # По умолчанию – исполнитель
        )

    # Генерируем JWT-токен
    token = create_jwt_token(user.user_id)

    return {"user": UserSchema.from_orm(user), "token": token}


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
