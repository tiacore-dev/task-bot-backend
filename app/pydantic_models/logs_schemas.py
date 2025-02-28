from pydantic import BaseModel, UUID4


class UserActivityLogSchema(BaseModel):
    log_id: UUID4
    user_id: UUID4
    action: str
    timestamp: str


class UserActivityLogCreateSchema(BaseModel):
    user_id: UUID4
    action: str
