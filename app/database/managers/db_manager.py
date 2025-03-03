from app.database.models import User
from tortoise.exceptions import DoesNotExist


async def get_user_by_telegram_id(telegram_id: int):
    """
    Получить пользователя по Telegram ID.
    """
    try:
        return await User.get(telegram_id=telegram_id)
    except DoesNotExist:
        return None
