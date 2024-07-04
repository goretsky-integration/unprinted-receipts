from collections.abc import Mapping

import httpx

from logger import create_logger
from new_types import DodoIsHttpClient

__all__ = ('DodoIsConnection',)

logger = create_logger('dodo_is_connection')


class DodoIsConnection:

    def __init__(self, http_client: DodoIsHttpClient):
        self.__http_client = http_client

    async def get_shift_management_partial_index(
            self,
            *,
            cookies: Mapping[str, str],
            unit_name: str,
    ) -> httpx.Response:
        url = '/Managment/ShiftManagment/PartialIndex'

        logger.debug(
            'Requesting shift management partial index',
            extra={'unit_name': unit_name},
        )
        response = await self.__http_client.get(
            url=url,
            cookies=dict(cookies),
        )
        logger.info(
            'Shift management partial index response received',
            extra={
                'unit_name': unit_name,
                'status_code': response.status_code,
                'response_body': response.text,
            },
        )

        return response

    async def get_unprinted_receipts(
            self,
            *,
            cookies: Mapping[str, str],
            cash_box_id: int,
            shift_id: int,
            unit_name: str,
    ) -> httpx.Response:
        url = '/Managment/ShiftManagment/ZReport'
        query_params = {'cashBoxId': cash_box_id, 'shiftId': shift_id}

        logger.debug(
            'Requesting unprinted receipts',
            extra={
                'query_params': query_params,
                'unit_name': unit_name,
            },
        )
        response = await self.__http_client.get(
            url=url,
            params=query_params,
            cookies=dict(cookies),
        )

        logger.info(
            'Unprinted receipts response received',
            extra={
                'unit_name': unit_name,
                'query_params': query_params,
                'status_code': response.status_code,
                'response_body': response.text,
            },
        )

        return response
