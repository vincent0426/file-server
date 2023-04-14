import fastapi


def register_routers(app: fastapi.FastAPI):
    from . import (
        account,
        file,
        pub_key,
        public,
    )

    app.include_router(public.router)
    app.include_router(account.router)
    app.include_router(file.router)
    app.include_router(pub_key.router)
    
