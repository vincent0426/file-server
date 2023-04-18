import fastapi

from . import s3_file


def register_routers(app: fastapi.FastAPI):
    from . import (
        account,
        pub_key,
        public,
        s3_file,
        transaction,
    )

    app.include_router(public.router)
    app.include_router(account.router)
    app.include_router(s3_file.router)
    app.include_router(pub_key.router)
    app.include_router(transaction.router)
    
