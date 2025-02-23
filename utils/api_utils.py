# utils/api_utils.py
import functools
import logging
from typing import Callable, Any

def async_openai_error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """Asynchronous decorator to handle OpenAI API errors.

    Args:
        func (Callable[..., Any]): Function to decorate.

    Returns:
        Callable[..., Any]: Wrapped function.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.getLogger(__name__).error(f"OpenAI API error: {e}")
            raise e
    return wrapper

def sync_openai_error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """Synchronous decorator to handle OpenAI API errors.

    Args:
        func (Callable[..., Any]): Function to decorate.

    Returns:
        Callable[..., Any]: Wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.getLogger(__name__).error(f"OpenAI API error: {e}")
            raise e
    return wrapper
