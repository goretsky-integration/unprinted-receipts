import datetime
from collections.abc import AsyncGenerator
from uuid import UUID

import httpx

from new_types import DodoIsHttpClient

__all__ = ('DodoIsConnection',)


class DodoIsConnection:

    def __init__(self, http_client: DodoIsHttpClient):
        self.__http_client = http_client

    async def iter_partial_orders(
            self,
            *,
            cookies: dict[str, str],
            date: datetime.date,
            page: int = 1,
    ) -> AsyncGenerator[httpx.Response, None]:
        url = '/Managment/ShiftManagment/PartialShiftOrders'
        while True:
            query_params = {
                'page': page,
                'date': f'{date:%Y-%m-%d}',
                'orderStateFilter': 'Failure',
            }
            response = await self.__http_client.get(
                url=url,
                params=query_params,
                cookies=cookies,
            )
            yield response
            page += 1

    async def get_detailed_order(
            self,
            *,
            cookies: dict[str, str],
            order_id: UUID,
    ) -> httpx.Response:
        url = '/Managment/ShiftManagment/Order'
        query_params = {'orderUUId': order_id.hex}
        response = await self.__http_client.get(
            url=url,
            params=query_params,
            cookies=cookies,
        )
        return response
