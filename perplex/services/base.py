"""
Base service classes and utilities for MindMate-AI
"""
import os
import time
import logging
from abc import ABC, abstractmethod
from functools import wraps

logger = logging.getLogger(__name__)


class MissingConfigError(Exception):
    """
    Raised when a required environment variable is missing.
    
    Attributes:
        env_var: Name of the missing environment variable
        help_url: URL where user can get the required credential
    """
    def __init__(self, env_var: str, help_url: str):
        self.env_var = env_var
        self.help_url = help_url
        super().__init__(
            f"Missing required environment variable: {env_var}\n"
            f"  → Get credentials at: {help_url}"
        )


class ServiceHealthError(Exception):
    """
    Raised when a service health check fails.
    
    Attributes:
        service_name: Name of the service that failed
        details: Additional error details
    """
    def __init__(self, service_name: str, details: str):
        self.service_name = service_name
        self.details = details
        super().__init__(f"{service_name} health check failed: {details}")


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator that retries a function with exponential backoff on transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (doubles each retry)
    
    Retries on:
        - HTTP 429 (Rate Limited)
        - HTTP 503 (Service Unavailable)
        - Connection timeouts
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    is_retryable = any(term in error_str for term in [
                        '429', 'rate limit', 'too many requests',
                        '503', 'service unavailable', 'timeout', 'connection'
                    ])
                    
                    if not is_retryable or attempt == max_retries:
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"{func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s")
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class BaseService(ABC):
    """Abstract base class for all AI service implementations."""
    
    def _validate_env_var(self, name: str, help_url: str) -> str:
        """Validate that an environment variable exists and return its value."""
        value = os.getenv(name)
        if not value:
            raise MissingConfigError(name, help_url)
        return value
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify the service is properly configured and accessible."""
        pass
