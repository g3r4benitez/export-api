from fastapi import APIRouter

from app.controllers import export_controller as router_export
from app.controllers import ping_controller as ping
from app.core.config import API_PREFIX

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(router_export.router, tags=["export"], prefix="/exports")
api_router.include_router(ping.router, tags=["ping"], prefix="/ping")
