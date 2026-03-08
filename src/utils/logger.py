"""Structured logging for TraceGuard AI"""

import logging
import os
from pathlib import Path
from datetime import datetime


class TraceGuardLogger:
    """Centralized logging configuration for TraceGuard AI"""

    _loggers = {}

    @staticmethod
    def get_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
        """
        Get or create a logger with the specified configuration.

        Args:
            name: Logger name (typically __name__)
            log_file: Optional log file path
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Configured logger instance
        """
        if name in TraceGuardLogger._loggers:
            return TraceGuardLogger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        TraceGuardLogger._loggers[name] = logger
        return logger

    @staticmethod
    def setup_root_logger(log_dir: str = "./logs", level: str = "INFO"):
        """Setup root logger for the application"""
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"traceguard_{timestamp}.log")
        TraceGuardLogger.get_logger("traceguard", log_file, level)


# Convenience function for getting logger
def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a logger instance"""
    return TraceGuardLogger.get_logger(name, level=level)


def setup_logging(level: str = "INFO", log_dir: str = "./logs"):
    """
    Setup root logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"traceguard_{timestamp}.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    
    # Clear existing handlers and add new ones
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
