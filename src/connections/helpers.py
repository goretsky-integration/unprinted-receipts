import asyncio
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeAlias, TypeVar

import structlog.stdlib

__all__ = ('retry_on_failure',)

logger = structlog.stdlib.get_logger('app')

T = TypeVar("T")
P = ParamSpec('P')

Callback: TypeAlias = Callable[P, T]


def retry_on_failure(attempts: int) -> Callable[[Callback], Callback]:
    if attempts < 1:
        raise ValueError("Attempts must be greater than 0")

    def decorator(func: Callable) -> Callable:

        if not asyncio.iscoroutinefunction(func):
            raise ValueError('Function must be async')

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            for _ in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as error:
                    logger.warning(
                        f'Failed to execute "{func.__name__}"'
                        f' due to error: {error}',
                    )
            raise Exception(
                f'Failed to execute "{func.__name__}"'
                f' after {attempts} attempts'
            )

        return wrapper

    return decorator
