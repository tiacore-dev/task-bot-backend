from .account_route import account_router
from .tasks_route import tasks_router
from .auth_route import auth_router


def register_routes(app):
    app.include_router(account_router)
    app.include_router(tasks_router)
    app.include_router(auth_router)
