import asyncio
import itertools
from collections.abc import Coroutine, Iterable
from typing import Any, TypeVar

T = TypeVar('T')

__all__ = ('batched', 'execute_batched_tasks')


def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


async def execute_batched_tasks(
        tasks: Iterable[asyncio.Task[T] | Coroutine[Any, Any, T]],
        *,
        batch_size: int = 10,
) -> list[T | Exception]:
    result = []
    for tasks_batch in batched(tasks, n=batch_size):
        result += await asyncio.gather(*tasks_batch, return_exceptions=True)
    return result
