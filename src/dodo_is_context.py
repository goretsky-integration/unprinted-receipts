import datetime

from connections.dodo_is import DodoIsConnection
from models import DetailedOrder, PartialOrder
from parsers import parse_detailed_order_response, parse_partial_orders_response


class DodoIsContext:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__dodo_is_connection = dodo_is_connection

    async def get_partial_orders(
            self,
            *,
            date: datetime.date,
            cookies: dict[str, str],
    ):
        partial_orders_iterator = self.__dodo_is_connection.iter_partial_orders(
            cookies=cookies,
            date=date,
        )

        all_partial_orders: list[PartialOrder] = []
        async for response in partial_orders_iterator:
            partial_orders = parse_partial_orders_response(response)

            if not partial_orders:
                break

            all_partial_orders += partial_orders

        return all_partial_orders

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
        return parse_detailed_order_response(response, partial_order)
