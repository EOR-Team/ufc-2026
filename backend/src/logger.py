"""
Unified logger module with clean, readable output formatting.
Provides info, error, warning, and debug logging functions with color support.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with ANSI color codes for better readability."""

    # Color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Level color mapping
    LEVEL_COLORS = {
        "DEBUG": CYAN + DIM,
        "INFO": GREEN,
        "WARNING": YELLOW + BOLD,
        "ERROR": RED + BOLD,
        "CRITICAL": RED + BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and improved readability."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get color for the level
        level_color = self.LEVEL_COLORS.get(record.levelname, self.WHITE)
        level_name = f"{level_color}{record.levelname:8}{self.RESET}"

        # Format the message
        message = record.getMessage()

        # Build the formatted log line
        log_line = (
            f"{self.DIM}[{timestamp}]{self.RESET} "
            f"{level_name} "
            f"{self.BOLD}{record.name}{self.RESET}: "
            f"{message}"
        )

        # Add exception info if present
        if record.exc_info:
            log_line += f"\n{self.exc_text}"

        return log_line


# Global logger instance
_logger: Optional[logging.Logger] = None


def _get_logger() -> logging.Logger:
    """Get or create the global logger instance."""
    global _logger

    if _logger is not None:
        return _logger

    # Create logger
    _logger = logging.getLogger("ufc")
    _logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers
    if _logger.handlers:
        return _logger

    # Console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())
    _logger.addHandler(console_handler)

    return _logger


def setup_file_logging(log_dir: Optional[str] = None) -> None:
    """
    Setup file logging in addition to console logging.

    Args:
        log_dir: Directory to store log files. If None, uses './logs'
    """
    logger = _get_logger()

    if log_dir is None:
        log_dir = "logs"

    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create file handler
    log_file = log_path / f"ufc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # File formatter (no colors)
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def debug(message: str, *args, **kwargs) -> None:
    """
    Log a debug message.

    Args:
        message: The message to log
        *args: Format arguments
        **kwargs: Additional keyword arguments
    """
    _get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """
    Log an info message.

    Args:
        message: The message to log
        *args: Format arguments
        **kwargs: Additional keyword arguments
    """
    _get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """
    Log a warning message.

    Args:
        message: The message to log
        *args: Format arguments
        **kwargs: Additional keyword arguments
    """
    _get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, exc_info: bool = False, **kwargs) -> None:
    """
    Log an error message.

    Args:
        message: The message to log
        *args: Format arguments
        exc_info: If True, include exception traceback information
        **kwargs: Additional keyword arguments
    """
    _get_logger().error(message, *args, exc_info=exc_info, **kwargs)


def critical(message: str, *args, exc_info: bool = False, **kwargs) -> None:
    """
    Log a critical message.

    Args:
        message: The message to log
        *args: Format arguments
        exc_info: If True, include exception traceback information
        **kwargs: Additional keyword arguments
    """
    _get_logger().critical(message, *args, exc_info=exc_info, **kwargs)


# Convenience aliases
warn = warning  # Alias for backward compatibility
err = error  # Alias for backward compatibility
