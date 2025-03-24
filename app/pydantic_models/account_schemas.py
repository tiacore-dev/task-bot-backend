from pydantic import BaseModel, UUID4


class UserAccountSchema(BaseModel):
    account_id: UUID4  # BigInteger
    user: UUID4
    platform: UUID4
    account_name: str
    account_platform_id: str


class UserAccountCreateSchema(BaseModel):
    platform: UUID4
    account_name: str
    account_platform_id: str


class UserAccountUpdateSchema(BaseModel):
    platform: UUID4
    account_name: str
    account_platform_id: str
