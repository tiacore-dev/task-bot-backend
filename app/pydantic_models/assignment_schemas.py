from typing import Optional
from pydantic import BaseModel, UUID4


# Полученное задание (исполнитель взял задание)
class TaskAssignmentSchema(BaseModel):
    assignment_id: UUID4
    user_id: UUID4
    task_id: UUID4
    assigned_profile_id: int  # ID аккаунта пользователя
    submitted_at: Optional[str]
    status: str


class TaskAssignmentCreateSchema(BaseModel):
    user_id: UUID4
    task_id: UUID4
    assigned_profile_id: int
