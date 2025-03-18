from fastapi import APIRouter, HTTPException, Depends
from app.pydantic_models.task_schemas import TaskSchema
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import Task, TaskAssignment, User

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

# 📌 Получить список всех доступных заданий


@tasks_router.get("/", response_model=list[TaskSchema])
async def get_available_tasks():
    """ Возвращает список активных заданий. """
    tasks = await Task.filter(status="active").all()
    return [TaskSchema.model_validate(task) for task in tasks]


@tasks_router.post("/{task_id}/accept")
async def accept_task(task_id: str, telegram_id: int):
    """ Пользователь берет задание в работу. """
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = await Task.get_or_none(task_id=task_id, status="active")
    if not task:
        raise HTTPException(
            status_code=404, detail="Task not found or unavailable")

    # Проверяем, не взято ли уже это задание
    existing_assignment = await TaskAssignment.get_or_none(task_id=task_id, user_id=user.user_id)
    if existing_assignment:
        raise HTTPException(
            status_code=400, detail="You already accepted this task")

    await TaskAssignment.create(user_id=user.user_id, task_id=task_id, status="in_progress")
    return {"message": "Task accepted"}


# 📌 Сдать задание на проверку
@tasks_router.post("/{task_id}/submit")
async def submit_task(task_id: str, user: User = Depends(get_user_by_telegram_id)):
    """
    Отправляет задание на проверку.
    """
    assignment = await TaskAssignment.get_or_none(task_id=task_id, user_id=user.user_id, status="in_progress")
    if not assignment:
        raise HTTPException(
            status_code=404, detail="Task not found or already submitted")

    assignment.status = "pending_review"
    await assignment.save()
    return {"message": "Task submitted for review"}

# 📌 Получить список моих заданий


@tasks_router.get("/my", response_model=list[TaskSchema])
async def get_my_tasks(user: User = Depends(get_user_by_telegram_id)):
    """
    Получает список заданий пользователя.
    """
    assignments = await TaskAssignment.filter(user_id=user.user_id).prefetch_related("task")
    return [TaskSchema.model_validate(assignment.task) for assignment in assignments]
