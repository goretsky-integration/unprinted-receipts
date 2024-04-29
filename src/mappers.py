import itertools
import operator
from collections.abc import Iterable, Mapping
from typing import TypeAlias

import structlog.stdlib

from enums import CountryCode
from models import DetailedOrder
from models.events import Event, EventPayload

__all__ = ('prepare_events', 'group_orders_by_unit_name')

logger = structlog.stdlib.get_logger('app')

DetailedOrders: TypeAlias = Iterable[DetailedOrder]
OrdersGroupedByUnitName: TypeAlias = Iterable[tuple[str, DetailedOrders]]


def group_orders_by_unit_name(
        orders: Iterable[DetailedOrder],
) -> OrdersGroupedByUnitName:
    return itertools.groupby(
        iterable=orders,
        key=operator.attrgetter('unit_name')
    )


def prepare_events(
        *,
        unit_name_to_id: Mapping[str, int],
        canceled_orders: Iterable[DetailedOrder],
        country_code: CountryCode,
) -> list[Event]:
    unit_name_and_canceled_orders = group_orders_by_unit_name(canceled_orders)
    events: list[Event] = []

    for unit_name, grouped_canceled_orders in unit_name_and_canceled_orders:

        try:
            unit_id = unit_name_to_id[unit_name]
        except KeyError:
            logger.warning(
                'No unit_id found for unit_name',
                unit_name=unit_name,
            )
            continue

        event_payload = EventPayload(
            orders=list(grouped_canceled_orders),
            unit_name=unit_name,
            country_code=country_code,
        )
        event = Event(unit_ids=[unit_id], payload=event_payload)
        events.append(event)

    return events
