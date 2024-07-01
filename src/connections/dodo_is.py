from collections.abc import Mapping

import httpx

from new_types import DodoIsHttpClient

__all__ = ('DodoIsConnection',)


class DodoIsConnection:

    def __init__(self, http_client: DodoIsHttpClient):
        self.__http_client = http_client

    async def get_shift_management_partial_index(
            self,
            *,
            cookies: Mapping[str, str],
    ) -> httpx.Response:
        url = '/Managment/ShiftManagment/PartialIndex'

        response = await self.__http_client.get(
            url=url,
            cookies=dict(cookies),
        )

        return response

    async def get_unprinted_receipts(
            self,
            *,
            cookies: Mapping[str, str],
            cash_box_id: int,
            shift_id: int,
    ) -> httpx.Response:
        url = '/Managment/ShiftManagment/ZReport'
        query_params = {'cashBoxId': cash_box_id, 'shift_id': shift_id}

        response = await self.__http_client.get(
            url=url,
            params=query_params,
            cookies=dict(cookies),
        )

        return response
