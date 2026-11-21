import time
from flask import Blueprint, jsonify
from prometheus_client import Gauge, Histogram
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models import db

health_bp = Blueprint("health", __name__)

DB_UP = Gauge(
    "servicedesk_db_up",
    "Database availability status from active SELECT 1 probe (1 = up, 0 = down)",
)

DB_HEALTH_DURATION_SECONDS = Histogram(
    "servicedesk_db_health_check_duration_seconds",
    "Execution duration of the SELECT 1 database health check in seconds",
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)


@health_bp.route("/health", methods=["GET"])
def health_check():
    start_time = time.perf_counter()
    try:
        db.session.execute(text("SELECT 1"))
        elapsed_seconds = time.perf_counter() - start_time
        elapsed_ms = round(elapsed_seconds * 1000, 3)

        DB_UP.set(1)
        DB_HEALTH_DURATION_SECONDS.observe(elapsed_seconds)

        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "servicedesk-api",
                    "database": {
                        "status": "up",
                        "latency_ms": elapsed_ms,
                    },
                }
            ),
            200,
        )
    except SQLAlchemyError as exc:
        db.session.rollback()
        elapsed_seconds = time.perf_counter() - start_time
        elapsed_ms = round(elapsed_seconds * 1000, 3)

        DB_UP.set(0)
        DB_HEALTH_DURATION_SECONDS.observe(elapsed_seconds)

        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "service": "servicedesk-api",
                    "database": {
                        "status": "down",
                        "latency_ms": elapsed_ms,
                        "error": str(exc.__class__.__name__),
                    },
                }
            ),
            503,
        )