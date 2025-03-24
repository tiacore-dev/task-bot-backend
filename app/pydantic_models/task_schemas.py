from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, UUID4


# Платформа для заданий
class TaskPlatformSchema(BaseModel):
    platform_id: UUID4
    name: str


class TaskTypeSchema(BaseModel):
    task_type_id: str
    name: str


class TaskStatusSchema(BaseModel):
    status_id: str
    name: str

# Задание (отображение)


class TaskSchema(BaseModel):
    task_id: UUID4
    creator_id: UUID4
    platform_id: UUID4
    task_type_id: str
    description: str
    reward: Decimal
    verification_type: str
    status_id: str

# Создание задания


class TaskCreateSchema(BaseModel):
    creator_id: UUID4
    platform_id: UUID4
    task_type_id: str
    description: str
    reward: Decimal
    verification_type: str
    status_id: str

# Обновление задания

# Мои задания


class MyTaskSchema(BaseModel):
    assignment_id: UUID4
    task_id: UUID4
    description: str
    reward: int
    status_id: str


class TaskUpdateSchema(BaseModel):
    description: Optional[str] = None
    reward: Optional[Decimal] = None
    status_id: Optional[str] = None


class AcceptTaskRequest(BaseModel):
    account_id: UUID4
