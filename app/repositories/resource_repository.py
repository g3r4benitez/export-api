from app.core.config import get_connection


def get_type(cd_resource: int):
    """Return type of resource"""

    conn = get_connection()

    parameters = [cd_resource]

    query = "select cd_community_entity_type from resource  where idresource = %s "

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, parameters)
            row = cursor.fetchone()
            return row[0]

