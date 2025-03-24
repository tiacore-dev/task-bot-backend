from uuid import UUID
from loguru import logger
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.pydantic_models.task_schemas import TaskSchema, AcceptTaskRequest, MyTaskSchema
from app.pydantic_models.transaction_schemas import TransactionSchema
from app.s3.s3_manager import AsyncS3Manager
from app.database.managers.db_manager import get_user_by_telegram_id
from app.database.models import Task, TaskAssignment, User, Transaction, UserAccount, TaskVerification


tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

# 📌 Получить список всех доступных заданий


@tasks_router.get("/", response_model=list[TaskSchema])
async def get_available_tasks(telegram_id: int):
    """ Возвращает список активных заданий, которые пользователь ещё не принял. """
    try:
        user = await User.get_or_none(telegram_id=telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем ID уже принятых заданий
        taken_task_ids = await TaskAssignment.filter(user=user.user_id).values_list("task_id", flat=True)

        # Ищем задания со статусом active, исключая уже принятые
        tasks = await Task.filter(status="active").exclude(task_id__in=taken_task_ids).all().values()

        return [TaskSchema(**task) for task in tasks]

    except HTTPException as http_err:
        logger.warning(f"⚠️ {http_err.detail}")
        return JSONResponse(status_code=http_err.status_code, content={"error": http_err.detail})
    except Exception as e:
        logger.exception(f"Ошибка при получении доступных заданий: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# 📌 Принять задание


@tasks_router.post("/{task_id}/accept")
async def accept_task(
    task_id: str,
    telegram_id: int,
    data: AcceptTaskRequest
):
    """ Пользователь берет задание в работу. """
    logger.info(
        f"📌 Принятие задания {task_id} пользователем с telegram_id={telegram_id}")

    try:
        # Логируем входные данные
        if not task_id:
            logger.warning("❌ Ошибка: task_id не передан")
            raise HTTPException(status_code=400, detail="Task ID is required")

        if not telegram_id:
            logger.warning("❌ Ошибка: telegram_id не передан")
            raise HTTPException(
                status_code=400, detail="Telegram ID is required")

        # Проверяем существование пользователя
        user = await User.get_or_none(telegram_id=telegram_id)
        if not user:
            logger.warning(
                f"❌ Ошибка: Пользователь с telegram_id={telegram_id} не найден")
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем существование задания
        task = await Task.get_or_none(task_id=task_id, status="active")
        if not task:
            logger.warning(
                f"❌ Ошибка: Задание {task_id} не найдено или уже недоступно")
            raise HTTPException(
                status_code=404, detail="Task not found or unavailable")

        # Проверяем, не взял ли пользователь уже это задание
        existing_assignment = await TaskAssignment.get_or_none(task=task_id, user=user.user_id)
        if existing_assignment:
            logger.warning(
                f"❌ Ошибка: Пользователь {telegram_id} уже взял задание {task_id}")
            raise HTTPException(
                status_code=400, detail="You already accepted this task")
        account = await UserAccount.get_or_none(account_id=data.account_id)
        if not account:
            logger.warning("❌ Аккаунт не найден")
            raise HTTPException(status_code=404, detail="Account not found")
        # Создаем запись о принятии задания
        await TaskAssignment.create(user_id=user.user_id, task=task, status="in_progress", assigned_profile=account)

        logger.info(
            f"✅ Успех: Пользователь {telegram_id} принял задание {task_id}")
        return {"message": "Task accepted"}

    except HTTPException as http_err:
        logger.error(
            f"❌ HTTPException: {http_err.detail} (код {http_err.status_code})")
        return JSONResponse(status_code=http_err.status_code, content={"error": http_err.detail})

    except Exception as e:
        logger.exception(f"❌ Ошибка при принятии задания: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

# 📌 Сдать задание на проверку


@tasks_router.post("/{task_id}/submit")
async def submit_task(
    task_id: UUID,
    assignment_id: UUID = Form(...),
    details: str = Form(None),
    screenshot: UploadFile = File(...),
    user: User = Depends(get_user_by_telegram_id)
):
    try:
        logger.info(
            f"📤 Пользователь {user.telegram_id} отправляет выполнение задания {task_id} (assignment_id={assignment_id})")
        assignment = await TaskAssignment.get_or_none(
            assignment_id=assignment_id
        )
        if not assignment:
            raise HTTPException(
                status_code=404, detail="Task not found or already submitted"
            )

        # Обновляем статус
        assignment.status = "pending_review"
        await assignment.save()

        # Загрузка скриншота
        file_bytes = await screenshot.read()
        filename = screenshot.filename or "screenshot.png"

        s3 = AsyncS3Manager()
        s3_key = await s3.upload_bytes(file_bytes, user.telegram_id, filename)

        # Создание верификации
        await TaskVerification.create(
            task_assignment=assignment,
            status="pending",
            details=details,
            s3_name=s3_key
        )

        return {"message": "Task submitted for review"}

    except HTTPException as http_err:
        return JSONResponse(status_code=http_err.status_code, content={"error": http_err.detail})

    except Exception as e:
        logger.exception(f"❌ Ошибка при сдаче задания: {e}")
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {e}"})


# 📌 Получить список моих заданий


@tasks_router.get("/my", response_model=list[MyTaskSchema])
async def get_my_tasks(user: User = Depends(get_user_by_telegram_id)):
    """
    Получает список заданий пользователя.
    """
    try:
        assignments = await TaskAssignment.filter(user=user.user_id).prefetch_related("task__status").all()

        result = []
        for a in assignments:
            task = await a.task  # принудительно получаем task
            result.append(MyTaskSchema(
                assignment_id=a.assignment_id,
                task_id=task.task_id,
                description=task.description,
                reward=task.reward,
                status_id=task.status.status_id,
            ))
        return result

    except Exception as e:
        logger.error(
            f"Ошибка при получении списка заданий пользователя: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@tasks_router.get("/completed", response_model=list[TaskSchema])
async def get_my_completed_tasks(user: User = Depends(get_user_by_telegram_id)):
    """
    Получает список заданий пользователя.
    """
    try:
        assignments = await TaskAssignment.filter(user=user.user_id, status="completed").prefetch_related("task").values()
        return [TaskSchema(**assignment.task) for assignment in assignments]
    except Exception as e:
        logger.error(
            f"Ошибка при получении списка заданий пользователя: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@tasks_router.get("/history", response_model=list[TransactionSchema])
async def get_my_transaction_history(user: User = Depends(get_user_by_telegram_id)):
    """
    Получает список заданий пользователя.
    """
    try:
        transactions = await Transaction.filter(user=user.user_id).prefetch_related("task").values()
        return [TransactionSchema(**transaction) for transaction in transactions]
    except Exception as e:
        logger.error(
            f"Ошибка при получении списка заданий пользователя: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@tasks_router.get("/{task_id}", response_model=TaskSchema)
async def get_task_by_id(task_id: str, user: User = Depends(get_user_by_telegram_id)):
    """ Возвращает задание по ID. """
    try:
        task = await Task.get_or_none(task_id=task_id).values()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskSchema(**task)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Ошибка при получении задания: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
