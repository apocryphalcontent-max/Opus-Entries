"""
OPUS MAXIMUS - Error Handling Framework
========================================
Comprehensive error handling with retry logic and graceful degradation.
"""

import logging
import time
import traceback
from functools import wraps
from typing import Callable, Any, Optional, Tuple, Type

logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class OpusError(Exception):
    """Base exception for all Opus Maximus errors"""
    pass


class GenerationError(OpusError):
    """Base exception for generation errors"""
    pass


class ValidationError(GenerationError):
    """Validation failed"""
    pass


class LLMError(GenerationError):
    """LLM generation failed"""
    pass


class ConfigurationError(OpusError):
    """Configuration is invalid"""
    pass


class ResourceError(OpusError):
    """Resource (memory, disk, etc.) error"""
    pass


class RetryExhausted(GenerationError):
    """All retry attempts exhausted"""
    pass


class CheckpointError(OpusError):
    """Checkpoint save/load failed"""
    pass


# ============================================================================
# RETRY DECORATORS
# ============================================================================

def retry_with_backoff(
    max_retries: int = 5,
    backoff_factor: float = 1.5,
    max_wait: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
        max_wait: Maximum wait time between retries
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @retry_with_backoff(max_retries=3, exceptions=(LLMError,))
        def generate_text(prompt):
            # ... LLM call that might fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            wait_time = 1.0

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}: {e}"
                        )
                        raise RetryExhausted(
                            f"Failed after {max_retries} attempts: {str(e)}"
                        ) from e

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for "
                        f"{func.__name__}: {e}"
                    )

                    # Calculate wait time with exponential backoff
                    current_wait = min(wait_time, max_wait)
                    logger.info(f"Retrying in {current_wait:.1f} seconds...")
                    time.sleep(current_wait)

                    wait_time *= backoff_factor

        return wrapper
    return decorator


def safe_execute(
    fallback_value: Optional[Any] = None,
    log_traceback: bool = True
):
    """
    Decorator for safe execution with fallback value.

    Args:
        fallback_value: Value to return if function fails
        log_traceback: Whether to log full traceback

    Example:
        @safe_execute(fallback_value="")
        def generate_section(prompt):
            # ... generation that might fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Execution failed in {func.__name__}: {e}")

                if log_traceback:
                    logger.debug(f"Traceback:\n{traceback.format_exc()}")

                if fallback_value is not None:
                    logger.info(f"Using fallback value for {func.__name__}")
                    return fallback_value
                else:
                    raise

        return wrapper
    return decorator


def timeout(seconds: float):
    """
    Decorator for timeout enforcement (Unix only).

    Note: This uses signal.alarm which only works on Unix systems.
    For cross-platform timeout, use concurrent.futures.TimeoutError.

    Args:
        seconds: Maximum execution time in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(
                    f"{func.__name__} exceeded timeout of {seconds}s"
                )

            # Set the signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the old signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper
    return decorator


# ============================================================================
# ERROR CONTEXT MANAGER
# ============================================================================

class ErrorContext:
    """
    Context manager for structured error handling with logging.

    Example:
        with ErrorContext("Generating section", subject="Theosis"):
            section = generate_section(...)
    """

    def __init__(
        self,
        operation: str,
        raise_on_error: bool = True,
        log_level: int = logging.ERROR,
        **context_data
    ):
        self.operation = operation
        self.raise_on_error = raise_on_error
        self.log_level = log_level
        self.context_data = context_data
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting: {self.operation}")
        if self.context_data:
            logger.debug(f"Context: {self.context_data}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time

        if exc_type is None:
            logger.info(
                f"Completed: {self.operation} in {elapsed:.2f}s"
            )
            return True
        else:
            logger.log(
                self.log_level,
                f"Failed: {self.operation} after {elapsed:.2f}s - {exc_val}"
            )

            if self.context_data:
                logger.debug(f"Failure context: {self.context_data}")

            if not self.raise_on_error:
                logger.info("Suppressing exception (raise_on_error=False)")
                return True  # Suppress exception

            return False  # Re-raise exception


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_config(config: dict, required_keys: list) -> None:
    """
    Validate configuration has all required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required key paths (e.g., "model.path")

    Raises:
        ConfigurationError: If required keys are missing
    """
    missing = []

    for key_path in required_keys:
        keys = key_path.split('.')
        current = config

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                missing.append(key_path)
                break
            current = current[key]

    if missing:
        raise ConfigurationError(
            f"Missing required configuration keys: {', '.join(missing)}"
        )


def validate_path(path, must_exist: bool = True, must_be_file: bool = False):
    """
    Validate file/directory path.

    Args:
        path: Path object or string
        must_exist: Whether path must already exist
        must_be_file: Whether path must be a file (vs directory)

    Raises:
        ConfigurationError: If validation fails
    """
    from pathlib import Path

    path = Path(path)

    if must_exist and not path.exists():
        raise ConfigurationError(f"Path does not exist: {path}")

    if must_be_file and path.exists() and not path.is_file():
        raise ConfigurationError(f"Path is not a file: {path}")


# ============================================================================
# RESOURCE MONITORING
# ============================================================================

class ResourceMonitor:
    """Monitor system resources and warn about potential issues"""

    @staticmethod
    def check_memory(required_gb: float) -> bool:
        """
        Check if sufficient memory is available.

        Args:
            required_gb: Required memory in GB

        Returns:
            True if sufficient memory available
        """
        try:
            import psutil
            available_gb = psutil.virtual_memory().available / (1024**3)

            if available_gb < required_gb:
                logger.warning(
                    f"Low memory: {available_gb:.1f}GB available, "
                    f"{required_gb:.1f}GB required"
                )
                return False

            return True

        except ImportError:
            logger.debug("psutil not available, skipping memory check")
            return True

    @staticmethod
    def check_disk_space(path, required_gb: float) -> bool:
        """
        Check if sufficient disk space is available.

        Args:
            path: Path to check
            required_gb: Required space in GB

        Returns:
            True if sufficient space available
        """
        try:
            import shutil
            from pathlib import Path

            path = Path(path)
            if not path.exists():
                path = path.parent

            stat = shutil.disk_usage(path)
            available_gb = stat.free / (1024**3)

            if available_gb < required_gb:
                logger.warning(
                    f"Low disk space: {available_gb:.1f}GB available, "
                    f"{required_gb:.1f}GB required"
                )
                return False

            return True

        except Exception as e:
            logger.debug(f"Could not check disk space: {e}")
            return True


# ============================================================================
# ERROR RECOVERY STRATEGIES
# ============================================================================

class ErrorRecoveryStrategy:
    """Strategies for recovering from different types of errors"""

    @staticmethod
    def handle_llm_error(error: Exception, attempt: int) -> str:
        """
        Determine recovery action for LLM errors.

        Returns:
            Recovery action: "retry", "fallback", "abort"
        """
        error_str = str(error).lower()

        # Out of memory - don't retry
        if "out of memory" in error_str or "oom" in error_str:
            logger.error("Out of memory error - cannot retry")
            return "abort"

        # Context length exceeded - try with shorter prompt
        if "context" in error_str or "too long" in error_str:
            if attempt < 3:
                logger.info("Context too long - will retry with shorter prompt")
                return "retry"
            return "abort"

        # Timeout - retry with backoff
        if "timeout" in error_str:
            logger.info("Timeout - will retry")
            return "retry"

        # Unknown error - retry a few times
        if attempt < 3:
            return "retry"

        return "abort"

    @staticmethod
    def handle_validation_error(
        error: ValidationError,
        attempt: int,
        max_attempts: int
    ) -> str:
        """
        Determine recovery action for validation errors.

        Returns:
            Recovery action: "regenerate", "fix", "accept", "abort"
        """
        # If we have attempts left, try to regenerate
        if attempt < max_attempts:
            logger.info(f"Validation failed, regenerating (attempt {attempt}/{max_attempts})")
            return "regenerate"

        # Out of attempts - check if errors are minor
        error_count = len(getattr(error, 'errors', []))
        if error_count < 3:
            logger.warning(f"Accepting output with {error_count} minor errors")
            return "accept"

        logger.error(f"Validation failed with {error_count} errors, aborting")
        return "abort"
