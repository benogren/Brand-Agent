"""
Cloud Logging Integration for AI Brand Studio.

Provides structured logging to Google Cloud Logging for production deployments.
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import Cloud Logging
try:
    from google.cloud import logging as cloud_logging
    from google.cloud.logging_v2.handlers import CloudLoggingHandler
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False


class BrandStudioLogger:
    """
    Custom logger for AI Brand Studio with Cloud Logging support.

    Features:
    - Structured logging with context
    - Cloud Logging integration (production)
    - Local file logging (development)
    - Agent workflow tracing
    """

    def __init__(
        self,
        name: str = "brand_studio",
        enable_cloud_logging: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize logger.

        Args:
            name: Logger name
            enable_cloud_logging: Enable Cloud Logging integration
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_console_handler()

        if enable_cloud_logging and CLOUD_LOGGING_AVAILABLE:
            self._setup_cloud_logging_handler()
        else:
            self._setup_file_handler()

    def _setup_console_handler(self):
        """Setup console logging handler."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format for console
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def _setup_file_handler(self):
        """Setup file logging handler for local development."""
        os.makedirs('logs', exist_ok=True)

        file_handler = logging.FileHandler(
            f'logs/{self.name}.log',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)

        # JSON format for file logs
        formatter = logging.Formatter(
            '%(message)s'  # We'll format as JSON in log methods
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _setup_cloud_logging_handler(self):
        """Setup Google Cloud Logging handler."""
        try:
            client = cloud_logging.Client()
            handler = CloudLoggingHandler(client, name=self.name)
            handler.setLevel(logging.INFO)

            self.logger.addHandler(handler)
            self.logger.info("Cloud Logging enabled")
        except Exception as e:
            self.logger.warning(f"Could not setup Cloud Logging: {e}")
            self._setup_file_handler()

    def _format_log_entry(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        event_type: str = "general"
    ) -> str:
        """
        Format log entry as structured JSON.

        Args:
            message: Log message
            context: Additional context
            event_type: Type of event

        Returns:
            JSON formatted log string
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": message,
            "event_type": event_type,
            "logger": self.name
        }

        if context:
            entry["context"] = context

        return json.dumps(entry)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        event_type: str = "general"
    ):
        """Log info message."""
        if context:
            self.logger.info(
                self._format_log_entry(message, context, event_type),
                extra=context
            )
        else:
            self.logger.info(message)

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        event_type: str = "debug"
    ):
        """Log debug message."""
        if context:
            self.logger.debug(
                self._format_log_entry(message, context, event_type),
                extra=context
            )
        else:
            self.logger.debug(message)

    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        event_type: str = "warning"
    ):
        """Log warning message."""
        if context:
            self.logger.warning(
                self._format_log_entry(message, context, event_type),
                extra=context
            )
        else:
            self.logger.warning(message)

    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        event_type: str = "error",
        exc_info: bool = False
    ):
        """Log error message."""
        if context:
            self.logger.error(
                self._format_log_entry(message, context, event_type),
                extra=context,
                exc_info=exc_info
            )
        else:
            self.logger.error(message, exc_info=exc_info)

    def agent_event(
        self,
        agent_name: str,
        event: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log agent-specific event.

        Args:
            agent_name: Name of the agent
            event: Event description
            details: Additional event details
        """
        context = {
            "agent": agent_name,
            "event": event
        }

        if details:
            context.update(details)

        self.info(
            f"[{agent_name}] {event}",
            context=context,
            event_type="agent_event"
        )

    def workflow_event(
        self,
        workflow_stage: str,
        status: str,
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log workflow stage event.

        Args:
            workflow_stage: Name of workflow stage
            status: Status (started, completed, failed)
            duration_ms: Duration in milliseconds
            details: Additional details
        """
        context = {
            "workflow_stage": workflow_stage,
            "status": status
        }

        if duration_ms is not None:
            context["duration_ms"] = duration_ms

        if details:
            context.update(details)

        self.info(
            f"Workflow: {workflow_stage} - {status}",
            context=context,
            event_type="workflow_event"
        )

    def generation_metrics(
        self,
        num_names_generated: int,
        num_validated: int,
        num_domain_available: int,
        avg_seo_score: float,
        session_id: str
    ):
        """
        Log brand name generation metrics.

        Args:
            num_names_generated: Number of names generated
            num_validated: Number passing validation
            num_domain_available: Number with .com available
            avg_seo_score: Average SEO score
            session_id: Session identifier
        """
        context = {
            "names_generated": num_names_generated,
            "names_validated": num_validated,
            "domains_available": num_domain_available,
            "avg_seo_score": avg_seo_score,
            "session_id": session_id
        }

        self.info(
            f"Generation metrics: {num_names_generated} names, {num_validated} validated",
            context=context,
            event_type="generation_metrics"
        )


# Singleton instance
_logger_instance: Optional[BrandStudioLogger] = None


def get_logger(
    name: str = "brand_studio",
    enable_cloud_logging: bool = None
) -> BrandStudioLogger:
    """
    Get or create the global BrandStudioLogger instance.

    Args:
        name: Logger name
        enable_cloud_logging: Enable Cloud Logging (auto-detect if None)

    Returns:
        BrandStudioLogger instance
    """
    global _logger_instance

    if _logger_instance is None:
        # Auto-detect cloud logging based on environment
        if enable_cloud_logging is None:
            enable_cloud_logging = os.getenv('ENABLE_CLOUD_LOGGING', 'false').lower() == 'true'

        log_level = os.getenv('LOG_LEVEL', 'INFO')

        _logger_instance = BrandStudioLogger(
            name=name,
            enable_cloud_logging=enable_cloud_logging,
            log_level=log_level
        )

    return _logger_instance


# Convenience function for standard Python logging compatibility
def setup_logging(
    enable_cloud_logging: bool = None,
    log_level: str = "INFO"
) -> logging.Logger:
    """
    Setup logging and return standard Python logger.

    Args:
        enable_cloud_logging: Enable Cloud Logging
        log_level: Log level

    Returns:
        Configured Python logger
    """
    logger = get_logger(
        enable_cloud_logging=enable_cloud_logging
    )

    return logger.logger
