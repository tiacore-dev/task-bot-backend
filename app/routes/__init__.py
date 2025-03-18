from .account_route import account_router
from .tasks_route import tasks_router


def register_routes(app):
    app.include_router(account_router)
    app.include_router(tasks_router)
