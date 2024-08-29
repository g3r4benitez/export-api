from app.core.config import get_connection


def get_types(cd_instance: int):
    """Return demographic data based on cd_resource and cd_instance"""

    conn = get_connection()

    parameters = [cd_instance]

    query = "select ic_has_business, ic_has_individuals from instances i where cd_instance = %s "

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, parameters)
            row = cursor.fetchone()
            return row[0], row[1]

