import datetime
from collections.abc import Iterable, Mapping

import structlog.stdlib

from connections.dodo_is import DodoIsConnection
from connections.helpers import retry_on_failure
from models import AccountCookies, DetailedOrder, PartialOrder
from parsers import DetailedOrderParser, parse_partial_orders_response
from tasks_executor import execute_batched_tasks

__all__ = ('DodoIsContext',)

logger = structlog.stdlib.get_logger('parser')


class DodoIsContext:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__dodo_is_connection = dodo_is_connection

    @retry_on_failure(attempts=5)
    async def get_partial_orders(
            self,
            *,
            date: datetime.date,
            account_cookies: AccountCookies,
    ):
        partial_orders_iterator = self.__dodo_is_connection.iter_partial_orders(
            cookies=account_cookies.cookies,
            date=date,
        )

        all_partial_orders: list[PartialOrder] = []
        async for response in partial_orders_iterator:
            partial_orders = parse_partial_orders_response(
                response=response,
                account_name=account_cookies.account_name,
            )

            if not partial_orders:
                break

            all_partial_orders += partial_orders

        return all_partial_orders

    async def get_partial_orders_batch(
            self,
            *,
            date: datetime.date,
            accounts_cookies: Iterable[AccountCookies],
    ) -> list[PartialOrder]:
        tasks = [
            self.get_partial_orders(
                date=date,
                account_cookies=account_cookies,
            )
            for account_cookies in accounts_cookies
        ]
        partial_orders_responses = await execute_batched_tasks(tasks)

        result: list[PartialOrder] = []
        for partial_orders_response in partial_orders_responses:
            if isinstance(partial_orders_response, Exception):
                logger.exception('Could not retrieve and parse partial orders')
            else:
                result += partial_orders_response

        return result

    async def get_detailed_order(
            self,
            *,
            cookies: dict[str, str],
            partial_order: PartialOrder,
    ) -> DetailedOrder:
        response = await self.__dodo_is_connection.get_detailed_order(
            cookies=cookies,
            order_id=partial_order.id,
        )
        parser = DetailedOrderParser(
            partial_order=partial_order,
            response=response,
        )
        return parser.parse()

    async def get_detailed_orders_batch(
            self,
            *,
            account_name_to_cookies: Mapping[str, dict[str, str]],
            partial_orders: Iterable[PartialOrder],
    ) -> list[DetailedOrder]:
        tasks = []
        for partial_order in partial_orders:
            try:
                cookies = account_name_to_cookies[partial_order.account_name]
            except KeyError:
                logger.error(
                    'No cookies found while retrieving detailed order',
                    account_name=partial_order.account_name,
                )
                continue

            tasks.append(
                self.get_detailed_order(
                    cookies=cookies,
                    partial_order=partial_order,
                ),
            )

        partial_order_responses = await execute_batched_tasks(tasks)

        result: list[DetailedOrder] = []
        for partial_order_response in partial_order_responses:
            if isinstance(partial_order_response, Exception):
                logger.error(
                    'Could not retrieve detailed order of partial order',
                )
            else:
                result.append(partial_order_response)

        return result
