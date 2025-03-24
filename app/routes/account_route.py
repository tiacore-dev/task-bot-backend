import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import User, UserAccount, TaskPlatform
from app.pydantic_models.user_schemas import UserSchema, UserCreateSchema
from app.pydantic_models.account_schemas import UserAccountCreateSchema, UserAccountSchema, UserAccountUpdateSchema


account_router = APIRouter(tags=["account"])

# 📌 2. Получение информации о текущем пользователе


@account_router.get("/accounts/me", response_model=UserSchema)
async def get_current_user(user: User = Depends(get_user_by_telegram_id)):
    # Конвертация Tortoise ORM в Pydantic
    return UserSchema.model_validate(user)


# 📌 3. Обновление информации о пользователе
@account_router.patch("/me", response_model=UserSchema)
async def update_user(data: UserCreateSchema, user: User = Depends(get_user_by_telegram_id)):
    """
    Обновление информации о пользователе (например, имени).
    """
    user.username = data.username or user.username
    await user.save()
    return user

# 📌 Обновление задания


@account_router.patch("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(account_id: UUID, account_data: UserAccountUpdateSchema, user: User = Depends(get_user_by_telegram_id)):
    account = await UserAccount.get_or_none(account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    updated_fields = account_data.dict(
        exclude_unset=True)  # Исключаем None-значения
    await account.update_from_dict(updated_fields)
    await account.save()

    return


@account_router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(account_id: UUID,  user: User = Depends(get_user_by_telegram_id)):
    account = await UserAccount.get_or_none(account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    await account.delete()

    return


# 📌 4. Привязка нового аккаунта соцсети


@account_router.post("/accounts", status_code=201)
async def add_account(account_data: UserAccountCreateSchema, user: User = Depends(get_user_by_telegram_id)):
    """
    Привязка соцсети (YouTube, Twitter, Telegram и т. д.).
    """
    try:
        logger.info(
            f"📥 Принимаем данные для привязки аккаунта: {account_data.dict()}")
        logger.info(f"🔍 Telegram ID пользователя: {user.telegram_id}")

        # Валидация платформы
        platform = await TaskPlatform.get_or_none(platform_id=account_data.platform)
        if platform:
            logger.info(
                f"✅ Платформа найдена: {platform.platform_name} ({platform.platform_id})")
        else:
            logger.warning(
                f"❌ Платформа с ID {account_data.platform} не найдена!")
            raise HTTPException(status_code=404, detail="Platform not found")

        # Повторная загрузка пользователя (опционально)
        # user = await User.get_or_none(user_id=user.user_id)
        # if not user:
        #     logger.warning(f"❌ Пользователь с ID {user.user_id} не найден!")
        #     raise HTTPException(status_code=404, detail="User not found")

        # Создание аккаунта
        await UserAccount.create(
            account_id=uuid.uuid4(),
            user=user,
            platform=platform,
            account_name=account_data.account_name,
            account_platform_id=account_data.account_platform_id,
        )

        logger.info(
            f"✅ Аккаунт успешно привязан для пользователя {user.user_id}")
        return {"message": "Account successfully linked"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.exception(f"❌ Ошибка при привязке аккаунта: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error") from e


# 📌 5. Получение всех привязанных соцсетей пользователя
@account_router.get("/accounts", response_model=list[UserAccountSchema])
async def get_accounts(user: User = Depends(get_user_by_telegram_id)):
    """
    Получение списка привязанных соцсетей.
    """
    accounts = await UserAccount.filter(user=user.user_id).all().values(
        "account_id",
        "user_id",
        "platform_id",
        "account_name",
        "account_platform_id",
    )

    return [UserAccountSchema(
        account_id=acc["account_id"],
        user=acc["user_id"],
        platform=acc["platform_id"],
        account_name=acc["account_name"],
        account_platform_id=acc["account_platform_id"],
    ) for acc in accounts]


@account_router.get("/platforms")
async def get_all_platforms():
    return await TaskPlatform.all().values("platform_id", "platform_name")
