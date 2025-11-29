"""
Monitoring utilities and Prometheus metrics integration.
"""
from __future__ import annotations

import time
from typing import Iterable

from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import connections, DatabaseError
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from accounts.utils import get_client_statistics

REQUEST_LATENCY = Histogram(
    'fintrack_request_latency_seconds',
    'Latency of HTTP requests in seconds',
    ['method', 'path'],
)
REQUEST_COUNT = Counter(
    'fintrack_request_total',
    'Total HTTP requests processed',
    ['method', 'path', 'status_code'],
)
ACTIVE_SESSIONS = Gauge(
    'fintrack_active_sessions',
    'Number of authenticated Django sessions',
)
ACTIVE_CLIENTS = Gauge('fintrack_active_clients', 'Number of active clients in the system')
PREMIUM_CLIENTS = Gauge('fintrack_premium_clients', 'Number of clients with premium access')
BASIC_CLIENTS = Gauge('fintrack_basic_clients', 'Number of clients with basic access')


def _should_track(path: str) -> bool:
    """Avoid collecting noisy metrics for static or health endpoints."""
    ignored_prefixes: Iterable[str] = getattr(settings, 'METRICS_IGNORE_PATH_PREFIXES', [])
    return not any(path.startswith(prefix) for prefix in ignored_prefixes)


class RequestMetricsMiddleware:
    """Collects request latency and throughput metrics."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_template = request.path
        if request.resolver_match and request.resolver_match.view_name:
            path_template = request.resolver_match.view_name

        track_request = _should_track(request.path)
        start = time.perf_counter()
        response = self.get_response(request)
        latency = time.perf_counter() - start

        if track_request:
            REQUEST_LATENCY.labels(request.method, path_template).observe(latency)
            REQUEST_COUNT.labels(request.method, path_template, response.status_code).inc()

        return response


def _update_business_metrics():
    """Push application-specific metrics into gauges prior to export."""
    stats = get_client_statistics()
    ACTIVE_CLIENTS.set(stats['active_clients'])
    PREMIUM_CLIENTS.set(stats['premium_clients'])
    BASIC_CLIENTS.set(stats['basic_clients'])

    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()
    ACTIVE_SESSIONS.set(active_sessions)


def metrics_view(_request):
    """Expose Prometheus metrics."""
    _update_business_metrics()
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


def health_check(_request):
    """Simple health check endpoint used by load tests and uptime monitors."""
    db_status = 'ok'
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
    except DatabaseError as exc:
        db_status = 'error'
        message = str(exc)
    else:
        message = 'healthy'

    payload = {
        'status': 'ok' if db_status == 'ok' else 'error',
        'database': db_status,
        'timestamp': timezone.now().isoformat(),
    }
    status_code = 200 if db_status == 'ok' else 500
    payload['detail'] = message
    return JsonResponse(payload, status=status_code)

