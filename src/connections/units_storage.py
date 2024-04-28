import httpx
import structlog

from new_types import UnitsStorageHttpClient

__all__ = ('UnitsStorageConnection',)

logger = structlog.stdlib.get_logger('app')


class UnitsStorageConnection:

    def __init__(self, http_client: UnitsStorageHttpClient):
        self.__http_client = http_client

    async def get_units(self) -> httpx.Response:
        url = '/units/'
        logger.debug('Retrieving units')
        response = await self.__http_client.get(url)
        logger.debug('Units retrieved', status_code=response.status_code)
        return response
