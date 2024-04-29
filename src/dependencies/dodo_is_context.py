from fast_depends import Depends

from connections.dodo_is import DodoIsConnection
from dependencies.connections import get_dodo_is_connection
from dodo_is_context import DodoIsContext

__all__ = ('get_dodo_is_context',)


async def get_dodo_is_context(
        dodo_is_connection: DodoIsConnection = Depends(get_dodo_is_connection),
) -> DodoIsContext:
    yield DodoIsContext(dodo_is_connection)
