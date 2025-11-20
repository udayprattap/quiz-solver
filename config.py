"""Configuration loader for environment variables.

Centralizes loading of EMAIL, SECRET, and optional PIPE_TOKEN.
Uses python-dotenv to load .env file. PIPE_TOKEN is optional and
should be used for authenticated outbound API calls if required.
"""

from __future__ import annotations
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load .env once here; other modules import values from this file
load_dotenv()

EMAIL: Optional[str] = os.getenv("EMAIL")
SECRET: Optional[str] = os.getenv("SECRET")
PIPE_TOKEN: Optional[str] = os.getenv("PIPE_TOKEN")


def validate_core_credentials() -> None:
    """Ensure mandatory credentials are present.

    Raises:
        ValueError: If EMAIL or SECRET are missing.
    """
    if not EMAIL or not SECRET:
        raise ValueError("EMAIL and SECRET environment variables are required. Add them to your .env file.")


def get_pipe_token() -> Optional[str]:
    """Return PIPE_TOKEN if configured.

    Returns:
        Optional[str]: The external PIPE token or None if not set.
    """
    return PIPE_TOKEN


def settings_summary(redact: bool = True) -> Dict[str, Any]:
    """Return a summary of loaded settings for debugging.

    Args:
        redact: Whether to redact sensitive tokens.

    Returns:
        Dict[str, Any]: Summary dictionary.
    """
    return {
        "EMAIL_set": bool(EMAIL),
        "SECRET_set": bool(SECRET),
        "PIPE_TOKEN_set": bool(PIPE_TOKEN),
        "PIPE_TOKEN_preview": (PIPE_TOKEN[:6] + "..." if PIPE_TOKEN and not redact else None)
    }
