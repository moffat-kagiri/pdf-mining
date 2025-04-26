from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryCallState
)
from typing import Type, Optional, Callable, Union
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger("retry_utils")
logger.setLevel(logging.INFO)

class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1,
        max_wait: float = 10,
        retry_on: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None,
        before_sleep: Optional[Callable[[RetryCallState], None]] = None
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.retry_on = retry_on or Exception
        self.before_sleep = before_sleep or self._default_before_sleep

    @staticmethod
    def _default_before_sleep(retry_state: RetryCallState) -> None:
        error_msg = str(retry_state.outcome.exception()) if retry_state.outcome else "No error info"
        logger.warning(
            f"Retry #{retry_state.attempt_number} failed. "
            f"Next attempt in {retry_state.next_action.sleep:.1f}s if available. "
            f"Last error: {error_msg}" if retry_state.next_action else
            f"Retry #{retry_state.attempt_number} failed (final attempt). "
            f"Last error: {error_msg}"
        )

def create_retry_decorator(config: RetryConfig) -> Callable:
    """Factory for tenacity retry decorators with custom config."""
    return retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=config.min_wait,
            max=config.max_wait
        ),
        retry=retry_if_exception_type(config.retry_on),
        before_sleep=config.before_sleep,
        reraise=True
    )

# Preconfigured retry decorators
retry_network = create_retry_decorator(
    RetryConfig(
        max_attempts=5,
        min_wait=2,
        retry_on=(ConnectionError, TimeoutError)
    )
)

retry_ocr = create_retry_decorator(
    RetryConfig(
        max_attempts=3,
        min_wait=0.5,
        retry_on=RuntimeError  # Tesseract/EasyOCR failures
    )
)

def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Custom callback for detailed retry logging."""
    if retry_state.attempt_number > 1:
        wait_time = f"{retry_state.next_action.sleep:.2f}s" if retry_state.next_action else "N/A"
        error_msg = type(retry_state.outcome.exception()).__name__ if retry_state.outcome else "No error info"
        logger.info(
            f"Attempt {retry_state.attempt_number} | "
            f"Wait: {wait_time} | "
            f"Last error: {error_msg}"
        )