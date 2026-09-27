"""Logging setup that never logs message contents or secrets."""

import logging


def configure_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(level=getattr(logging, level.upper()), format="%(levelname)s %(name)s: %(message)s")
    return logging.getLogger("telegram_ai_assistant")
