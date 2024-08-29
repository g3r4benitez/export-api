import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.initializer import init

from app.api.routes.router import api_router
from app.core.config import (APP_NAME, APP_VERSION,
                             IS_DEBUG)
from app.core.error_handler import HTTPCustomException, exception_handler, fatal_exception_handler


def start_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)
    # Routes
    fast_app.include_router(api_router)

    # Middleware
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Error handlers
    fast_app.add_exception_handler(HTTPCustomException, exception_handler)
    fast_app.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, fatal_exception_handler)
    return fast_app


app = start_app()
init(app)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
