"""Logging utilities for Koriel engine."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "time": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging(config: Dict[str, Any]) -> None:
    """Configure logging based on config."""
    monitoring = config.get("monitoring", {})
    level_name = str(monitoring.get("log_level", "INFO")).upper()
    if level_name in ("OFF", "NONE", "DISABLED"):
        logging.disable(logging.CRITICAL)
        return
    level = LOG_LEVELS.get(level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger("koriel")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get module-level logger."""
    return logging.getLogger(name)
