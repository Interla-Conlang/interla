"""
Logging configuration module for the Interla project.

This module provides a centralized logging configuration that can be imported
and used across all modules in the project.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging configuration for the entire project.

    Args:
        level: Logging level (default: DEBUG)
        format_string: Custom format string for log messages
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(levelname)s: %(message)s"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()
