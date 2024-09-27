from collections import defaultdict
from collections.abc import Iterable, Mapping
from functools import cached_property
from typing import Protocol, TypeVar
from uuid import UUID

from models import Event, EventPayload, Unit, Order

__all__ = (
    'prepare_events',
    'group_by_unit_uuid',
    'UnitsMapper',
)


class UnitsMapper:

    def __init__(self, units: Iterable[Unit]):
        self.__units = tuple(units)

    def __iter__(self) -> tuple[Unit, ...]:
        return self.__units

    @cached_property
    def uuids(self) -> list[UUID]:
        return [unit.uuid for unit in self.__units]

    @cached_property
    def uuid_to_account_name(self) -> dict[UUID, str]:
        return {unit.uuid: unit.account_name for unit in self.__units}

    @cached_property
    def account_name_to_units(self) -> dict[str, 'UnitsMapper']:
        account_name_to_units: dict[str, list[Unit]] = defaultdict(list)
        for unit in self.__units:
            account_name_to_units[unit.account_name].append(unit)
        return {
            account_name: UnitsMapper(units)
            for account_name, units in account_name_to_units.items()
        }

    @cached_property
    def uuid_to_name(self) -> dict[UUID, str]:
        return {unit.uuid: unit.name for unit in self.__units}


class HasUnitUUID(Protocol):
    unit_uuid: UUID


T = TypeVar('T', bound=HasUnitUUID)


def group_by_unit_uuid(
        items: Iterable[T],
) -> dict[UUID, list[T]]:
    unit_uuid_to_items: dict[UUID, list[T]] = defaultdict(list)
    for item in items:
        unit_uuid_to_items[item.unit_uuid].append(item)
    return dict(unit_uuid_to_items)


def prepare_events(
        *,
        unit_uuid_to_name: Mapping[UUID, str],
        orders: Iterable[Order],
) -> list[Event]:
    unit_name_to_orders = group_by_unit_uuid(orders)
    events: list[Event] = []

    for unit_uuid, grouped_orders in unit_name_to_orders.items():
        unit_name = unit_uuid_to_name[unit_uuid]

        event_payload = EventPayload(unit_name=unit_name, orders=grouped_orders)
        event = Event(unit_ids=unit_uuid, payload=event_payload)
        events.append(event)

    return events
