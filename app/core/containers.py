from dependency_injector import containers, providers
from app.services.export_service import ExportService


class ContainerService(containers.DeclarativeContainer):
    export_service = providers.Singleton(
        ExportService
    )