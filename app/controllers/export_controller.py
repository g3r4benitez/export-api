from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from starlette import status

from app.services.export_service import ExportService
from app.core.containers import ContainerService

router = APIRouter()


@router.post(
    "",
    name="export_update_sheets",
    status_code=status.HTTP_200_OK,
)
@inject
def update_sheets(
        export_service: ExportService = Depends(Provide[ContainerService.export_service]),
):
    export_service.update_sheets()
