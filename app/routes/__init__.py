from .account_route import account_router


def register_routes(app):
    app.include_router(account_router)
