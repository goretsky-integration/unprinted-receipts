import asyncio
import itertools
from collections.abc import AsyncGenerator, Coroutine, Iterable
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
        coroutines: Iterable[Coroutine[Any, Any, T]],
        *,
        batch_size: int = 10,
) -> AsyncGenerator[list[asyncio.Task[T]], None]:
    for coroutines_batch in batched(coroutines, n=batch_size):

        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(coroutine)
                for coroutine in coroutines_batch
            ]

        yield tasks
