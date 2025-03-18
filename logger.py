import sys
from loguru import logger
from app.database.models import UserActionLog


def setup_logger():

    # Конфигурация Loguru
    logger.remove()  # Удаляем стандартный обработчик
    logger.add(
        sys.stdout,  # Логи в консоль
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="DEBUG",
    )
    logger.add(
        "logs/app.log",  # Логи в файл
        rotation="10 MB",  # Ротация файла (каждые 10 MB)
        retention="7 days",  # Хранить логи 7 дней
        level="DEBUG",
        compression="zip",  # Сжимать старые логи
    )

# Если хотите, чтобы логгер вел себя как синглтон:


async def log_user_action(user_id: str, action: str, task_id: str = None):
    """
    Логирует действия пользователей в Telegram-приложении.
    """
    log_entry = await UserActionLog.create(
        user_id=user_id,
        action=action,
        task_id=task_id
    )
    print(f"✅ Лог добавлен: {log_entry}")
