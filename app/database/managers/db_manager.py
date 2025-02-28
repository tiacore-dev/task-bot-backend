from typing import Type, TypeVar, Optional, List
from loguru import logger
from tortoise.models import Model


# Создаем универсальный тип модели
T = TypeVar("T", bound=Model)


class BaseManager:
    def __init__(self, model: Type[T]):
        self.model = model
        logger.info(f"Initialized manager for model: {self.model.__name__}")

    async def get(self, **kwargs) -> Optional[T]:
        logger.info(f"Fetching a single record with filters: {kwargs}")
        result = await self.model.filter(**kwargs).first()
        if result:
            logger.info("Record fetched successfully")
        else:
            logger.warning("No record found")
        return result

    async def create(self, **kwargs) -> T:
        logger.info(f"Creating a new record with data: {kwargs}")
        try:
            instance = await self.model.create(**kwargs)
            logger.info(f"Record created successfully: {instance}")
            return instance
        except Exception as e:
            logger.error(f"Error creating record: {e}")
            raise

    async def update(self, obj: T, **kwargs) -> T:
        logger.info(f"Updating record {obj} with data: {kwargs}")
        try:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await obj.save()
            logger.info(f"Record updated successfully: {obj}")
            return obj
        except Exception as e:
            logger.error(f"Error updating record {obj}: {e}")
            raise

    async def delete(self, obj: T) -> None:
        logger.info(f"Deleting record: {obj}")
        try:
            await obj.delete()
            logger.info(f"Record deleted successfully: {obj}")
        except Exception as e:
            logger.error(f"Error deleting record {obj}: {e}")
            raise

    async def all(self) -> List[T]:
        logger.info("Fetching all records")
        try:
            records = await self.model.all()
            logger.info(f"Fetched {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"Error fetching all records: {e}")
            raise
