from typing import Optional
from pydantic import BaseModel, UUID4


class TaskVerificationSchema(BaseModel):
    verification_id: UUID4
    assignment_id: UUID4
    check_date: str
    status: str
    details: Optional[str] = None


class TaskVerificationCreateSchema(BaseModel):
    assignment_id: UUID4
    status: str
    details: Optional[str] = None
    screenshot: Optional[bytes] = None
