from pydantic import BaseModel, UUID4


class UserAccountSchema(BaseModel):
    account_id: int  # BigInteger
    user_id: UUID4
    platform: str
    account_name: str
    # ID в соцсети (переименован, чтобы не путать с account_id)
    account_platform_id: str


class UserAccountCreateSchema(BaseModel):
    user_id: UUID4
    platform: str
    account_name: str
    account_platform_id: str
