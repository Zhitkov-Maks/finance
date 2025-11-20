from django.db.models import Sum, Count, Avg
from django.db.models.functions import ExtractYear, ExtractMonth

from app_user.models import CustomUser
from transactions.models import Transaction

import os
from django.conf import settings
from django.db import connection

class SQLQueryService:
    """A class for an sql query for analytics."""
    @staticmethod
    def load_query(query_name):
        """Load SQL from a file."""
        query_path = os.path.join(
            settings.BASE_DIR,
            'analytics',
            'queries',
            f'{query_name}.sql'
        )
        with open(query_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def execute_query(query_name, params=None):
        """Execute SQL queries from a file."""
        sql = SQLQueryService.load_query(query_name)
        with connection.cursor() as cursor:
            cursor.execute(sql, params or [])
            return SQLQueryService._dictfetchall(cursor)

    @staticmethod
    def _dictfetchall(cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


class MonthlyAnalyticsService:
    """A service for making a request for analytics."""
    @staticmethod
    def get_analytics(user_id, year=None, type_tr='expense'):
        return SQLQueryService.execute_query(
            'monthly_analytics', 
            [user_id, type_tr, year, year]
        )
