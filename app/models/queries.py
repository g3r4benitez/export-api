from psycopg2.extensions import quote_ident
from app.core.config import COMMUNITY_ENTITY_TYPE_INDIVIDUAL, COMMUNITY_ENTITY_TYPE_BUSINESS

class Queries:
    @staticmethod
    def get_demographic():
        query = '''select
            d.uid
        from demographic d
        where
            d.cd_resource = %s
            and d.cd_instance = %s
        order by
            d.dt_created asc
            '''

        return query

    @staticmethod
    def get_document_types():
        query = '''select ds.ds_name as "Document Type" 
        from document_type dt
        '''
        return query

    @staticmethod
    def get_documents(document_types):
        query = '''select
            *
        from
            documents
        '''

        return query

    @staticmethod
    def get_business_documents(document_types):
        query = '''select
                *
            from
            business
            '''

        return query

