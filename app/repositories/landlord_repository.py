from celery.utils.log import get_task_logger

from app.core.config import get_connection
from app.models.queries import Queries

celery_log = get_task_logger(__name__)


def gets(cd_resource: int, cd_instance: int):
    """Return landlord info based on cd_resource and cd_instance"""

    celery_log.info(f"Running landlord tab for cd_resource={cd_resource} and cd_instance={cd_instance}")

    conn = get_connection()

    parameters = [cd_resource, cd_instance]

    query = Queries().get_landlord()

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, parameters)
            headers = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return headers, rows
