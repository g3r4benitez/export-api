from celery.utils.log import get_task_logger
import psycopg2

from app.core.config import get_connection
from app.models.queries import Queries

celery_log = get_task_logger(__name__)


def gets(cd_resource: int, cd_instance: int):
    """Return business questions based on cd_resource and cd_instance"""

    celery_log.info(f"Running bquestions tab for cd_resource={cd_resource} and cd_instance={cd_instance}")

    conn = get_connection()
    query_headers = Queries().get_header_bquestions(cd_resource, cd_instance)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query_headers)
            rows = cursor.fetchall()
            headers_list = []
            for row in rows:
                headers_list.append(row[0].replace("'", "''").replace('"', '-'))

            headers = ", ".join(f" \"{q}\" " for q in headers_list)
            headers_and_types = " text, ".join(f" \"{q}\" " for q in headers_list)

            # get the real query
            base_query = Queries().get_base_bquestions(cd_resource, cd_instance, headers, headers_and_types)
            try:

                cursor.execute(base_query)
                headers = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return headers, rows
            except psycopg2.errors.SyntaxError as e:
                celery_log.info("Can't write questions")
                celery_log.info(e)
                return ['No Questions'], [['', ], ]
