"""
logging_config.py — Structured JSON logging for Cloud Run.
No external dependencies — stdlib only.
Cloud Run ingests stdout as Cloud Logging; JSON fields are parsed automatically.
"""
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime


class CloudRunJsonFormatter(logging.Formatter):
    """JSON formatter compatible with Google Cloud Logging (structured logs)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[1]:
            payload["exception"] = str(record.exc_info[1])

        # Include logger name for filtering
        if record.name != "root":
            payload["logger"] = record.name

        # Include all extra fields passed via `extra={...}`
        for key in ("httpRequest", "user", "duration_ms", "trace_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(level: str | None = None) -> None:
    """
    Configure root logger with JSON formatting for Cloud Run.
    Call once at application startup.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to INFO,
               or DEBUG if LOG_LEVEL env var is set.
    """
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()

    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    # Remove existing handlers to avoid duplicates
    root.handlers.clear()

    # JSON handler on stdout (Cloud Run reads this)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CloudRunJsonFormatter())
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "requests", "googleapiclient", "chromadb", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging configured (level=%s, format=json)", level)


def request_middleware(app):
    """
    Flask before/after_request middleware that logs HTTP requests with timing.
    Injects `httpRequest` and `duration_ms` into the request-scoped logger.

    Usage:
        setup_logging()
        app = Flask(__name__)
        request_middleware(app)
    """
    import flask

    @app.before_request
    def _before():
        flask.g._request_start = time.perf_counter()

    @app.after_request
    def _after(response):
        duration = (time.perf_counter() - flask.g.pop("_request_start", time.perf_counter())) * 1000
        logger = logging.getLogger("http")

        # Only log non-static, non-health-check requests at INFO; health at DEBUG
        path = flask.request.path
        is_health = path in ("/health", "/healthz", "/")

        extra = {
            "httpRequest": {
                "requestMethod": flask.request.method,
                "requestUrl": path,
                "status": response.status_code,
                "userAgent": flask.request.headers.get("User-Agent", ""),
            },
            "duration_ms": round(duration, 2),
        }

        if response.status_code >= 500:
            logger.error("%s %s → %s (%.1fms)", flask.request.method, path, response.status_code, duration, extra=extra)
        elif response.status_code >= 400:
            logger.warning("%s %s → %s (%.1fms)", flask.request.method, path, response.status_code, duration, extra=extra)
        elif not is_health:
            logger.info("%s %s → %s (%.1fms)", flask.request.method, path, response.status_code, duration, extra=extra)

        return response
