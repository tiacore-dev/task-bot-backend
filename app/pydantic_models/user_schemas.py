from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, UUID4


# Роль пользователя


class UserRoleSchema(BaseModel):
    role_id: str
    name: str

# Пользователь (отображение)


class UserSchema(BaseModel):
    user_id: UUID4
    telegram_id: int
    username: Optional[str]
    role_id: str
    balance: Decimal
    referrer_id: Optional[UUID4]

# Создание пользователя


class UserCreateSchema(BaseModel):
    telegram_id: int
    username: Optional[str]
    role_id: str
    referrer_id: Optional[UUID4] = None

# Обновление баланса пользователя


class UserBalanceUpdateSchema(BaseModel):
    balance: Decimal
