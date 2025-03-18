import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

# Порт и биндинг
PORT = os.getenv('ADMIN_PORT', "8001")

# 📌 Автоматическое создание супер-админа


async def create_test_data():
    from app.database.models import UserRole
    try:
        await UserRole.create(role_id="executor", role_name="Исполнитель")
        await UserRole.create(role_id="manager", role_name="Проверяющий")
    except Exception as e:
        print(f"Exception: {e}")

app = create_app()

ORIGIN = os.getenv('ORIGIN')


@app.on_event("startup")
async def startup_event():
    # Создаем администратора при запуске
    await create_test_data()

# 📌 Запуск Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
