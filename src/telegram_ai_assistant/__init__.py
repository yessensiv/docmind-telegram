"""Offline DEMO_MODE implementation of Telegram AI Assistant."""

from .config import AssistantConfig, ConfigError, load_config
from .handlers import AssistantHandlers

__all__ = ["AssistantConfig", "AssistantHandlers", "ConfigError", "load_config"]
