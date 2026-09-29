"""
Server-Timing header: where each response spends its time, visible in the
browser devtools (Network → Timing) and with `curl -I`.

    Server-Timing: connect;dur=0.4, db;dur=12.3;desc="3 queries", app;dur=40.1, total;dur=52.8

- connect: opening the DB connection plus the health check (conn_health_checks).
- db: time inside SQL queries.
- app: everything else (views, templates, middleware).
"""
from time import perf_counter

from django.db import connection


class ServerTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = perf_counter()
        stats = {'queries': 0, 'db': 0.0}

        def timed(execute, sql, params, many, context):
            began = perf_counter()
            try:
                return execute(sql, params, many, context)
            finally:
                stats['queries'] += 1
                stats['db'] += perf_counter() - began

        if request.path.startswith(('/static/', '/media/')):
            return self.get_response(request)

        # Time the (lazy) connection + health check only when the request really uses the DB
        original_ensure = connection.ensure_connection

        def timed_ensure():
            began = perf_counter()
            try:
                return original_ensure()
            finally:
                stats['connect'] += perf_counter() - began

        stats['connect'] = 0.0
        connection.ensure_connection = timed_ensure
        try:
            with connection.execute_wrapper(timed):
                response = self.get_response(request)
        finally:
            del connection.ensure_connection  # back to the class method

        total = perf_counter() - start
        connect = stats['connect']
        app = max(total - connect - stats['db'], 0.0)
        response['Server-Timing'] = (
            f'connect;dur={connect * 1000:.1f}, '
            f'db;dur={stats["db"] * 1000:.1f};desc="{stats["queries"]} queries", '
            f'app;dur={app * 1000:.1f}, total;dur={total * 1000:.1f}'
        )
        return response
