"""Structured logging configuration."""
import logging
import sys
from app.config import settings


def setup_logging():
    """
    Configure structured logging for the application.
    
    Logs are written to stdout in a format suitable for production
    log aggregation systems (e.g., ELK, Splunk, CloudWatch).
    """
    
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set uvicorn loggers to same level
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    
    logging.info(
        f"Logging configured",
        extra={"log_level": settings.log_level}
    )
