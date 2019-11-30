"""Test runner."""

import os

import sqlparse
from django.conf import settings
from django.db import connection
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    """Custom test runner for initial SQL."""

    @staticmethod
    def execute_sql_from_file(filename="init.sql"):
        """Execute sql from file."""
        file_path = os.path.join(settings.SQL_PATH, filename)
        statements = sqlparse.split(open(file_path, "r").read())
        for stm in statements:
            with connection.cursor() as cur:
                if stm:
                    cur.execute(stm)

    def setup_databases(self, **kwargs):
        """Create test database and apply initial SQL."""
        test_db = super().setup_databases(**kwargs)
        self.execute_sql_from_file()
        return test_db
