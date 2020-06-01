from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    def _build_ads_query(self, filters):
        query_template = """
            SELECT
              ad.*
            FROM ad
            INNER JOIN car ON car.id = ad.car_id
            {where_clause}
        """
        where_clauses = []
        params = []

        for key, value in filters.items():
            where_clauses.append(f'{key} = ?')
            params.append(value)

        where_clause = ''
        if where_clauses:
            where_clause = 'WHERE {}'.format(' AND '.join(where_clauses))

        query = query_template.format(where_clause=where_clause)
        return query, params

    def get_ads(self, qs=None, user_id=None):
        filters = {}
        if qs:
            filters.update(qs)
        if user_id:
            filters['user_id'] = user_id
        query, params = self._build_ads_query(filters)
        cur = self.connection.execute(query, params)
        ads = cur.fetchall()
        return [dict(ad) for ad in ads]

    def get_ad(self, ad_id):
        query = (
            'SELECT * '
            'FROM ad '
            'WHERE id = ?'
        )
        params = (ad_id,)
        cur = self.connection.execute(query, params)
        ad = cur.fetchone()
        if ad is None:
            raise AdDoesNotExistError(ad_id)
        return dict(ad)
