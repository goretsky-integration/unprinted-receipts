from collections import defaultdict
from collections.abc import Iterable, Mapping
from uuid import UUID

from enums import CountryCode
from models import Event, EventPayload, OrderWithoutPrintedReceipt

__all__ = ('prepare_events', 'group_orders_by_unit_name')


def group_orders_by_unit_name(
        orders: Iterable[OrderWithoutPrintedReceipt],
) -> dict[str, list[OrderWithoutPrintedReceipt]]:
    unit_name_to_orders: dict[str, list[OrderWithoutPrintedReceipt]] = (
        defaultdict(list)
    )
    for order in orders:
        unit_name_to_orders[order.unit_name].append(order)
    return dict(unit_name_to_orders)


def prepare_events(
        *,
        unit_name_to_uuid: Mapping[str, UUID],
        orders: Iterable[OrderWithoutPrintedReceipt],
) -> list[Event]:
    unit_name_to_orders = group_orders_by_unit_name(orders)
    events: list[Event] = []

    for unit_name, grouped_canceled_orders in unit_name_to_orders.items():
        unit_uuid = unit_name_to_uuid[unit_name]

        event_payload = EventPayload(
            unit_name=unit_name,
            orders=grouped_canceled_orders,
        )
        event = Event(unit_ids=unit_uuid, payload=event_payload)
        events.append(event)

    return events
