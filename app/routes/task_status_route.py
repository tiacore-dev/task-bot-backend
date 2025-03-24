from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from app.pydantic_models.assignment_schemas import TaskAssignmentSchema
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import TaskAssignment, User


task_status_router = APIRouter(tags=["Assignment, Verification"])

# 📌 Получить список всех доступных заданий


@task_status_router.get("/assignments/{assignment_id}", response_model=TaskAssignmentSchema)
async def get_assignment_details(assignment_id: UUID, user: User = Depends(get_user_by_telegram_id)):
    assignment = await TaskAssignment.get_or_none(assignment_id=assignment_id).prefetch_related("task", "user")
    if not assignment or assignment.user.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return TaskAssignmentSchema(
        assignment_id=assignment.assignment_id,
        task_id=assignment.task.task_id,
        description=assignment.task.description,
        reward=assignment.task.reward,
        assignment_status=assignment.status,
    )
