import time
from flask import Blueprint, Response, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)

metrics_bp = Blueprint("metrics", __name__)

HTTP_REQUESTS_TOTAL = Counter(
    "servicedesk_http_requests_total",
    "Total HTTP requests processed by the Service Desk application",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "servicedesk_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


def init_metrics(app):
    """Attach request timing hooks and register the /metrics endpoint."""

    @app.before_request
    def _start_timer():
        request._prom_start_time = time.perf_counter()

    @app.after_request
    def _record_metrics(response):
        # Skip internal metrics scraping from inflating application traffic counters
        if request.path == "/metrics":
            return response

        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        method = request.method
        status = str(response.status_code)

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()

        start_time = getattr(request, "_prom_start_time", None)
        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(elapsed)

        return response

    app.register_blueprint(metrics_bp)


@metrics_bp.route("/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(data, mimetype=CONTENT_TYPE_LATEST)