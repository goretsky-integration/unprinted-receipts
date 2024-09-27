import httpx

from logger import create_logger
from new_types import DodoIsHttpClient

__all__ = ('DodoIsConnection',)

logger = create_logger('dodo_is_connection')


class DodoIsConnection:

    def __init__(self, http_client: DodoIsHttpClient):
        self.__http_client = http_client

    async def get_shifts(self, cookies: dict[str, str]) -> httpx.Response:
        url = '/api/shifts'
        query_params = {'page': 1, 'perPage': 1}

        response = await self.__http_client.get(
            url=url,
            params=query_params,
            cookies=cookies,
        )

        return response

    async def get_shift(
            self,
            shift_legacy_id: int,
            cookies: dict[str, str],
    ) -> httpx.Response:
        url = f'/api/shifts/{shift_legacy_id}'

        response = await self.__http_client.get(url=url, cookies=cookies)

        return response
