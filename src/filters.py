from collections.abc import Callable, Iterable
from functools import partial
from typing import TypeVar

from enums import SalesChannel
from models import DetailedOrder

__all__ = (
    'filter_shift_manager_account_names',
    'is_valid_canceled_order',
    'is_canceled_by_employee',
    'is_courier_assigned',
    'is_order_sales_channel',
    'all_lazy',
    'any_lazy',
    'filter_valid_canceled_orders',
)

T = TypeVar('T')


def filter_shift_manager_account_names(
        account_names: Iterable[str],
) -> list[str]:
    return [
        account_name for account_name in account_names
        if account_name.startswith('shift_manager')
    ]


def is_order_sales_channel(
        item: DetailedOrder,
        sales_channel: SalesChannel,
) -> bool:
    return item.sales_channel == sales_channel


def is_courier_assigned(item: DetailedOrder) -> bool:
    return item.courier_name is not None


def is_canceled_by_employee(item: DetailedOrder) -> bool:
    return item.canceled_by_user_name is not None


def all_lazy(*funcs: Callable[[T], bool]) -> Callable[[T], bool]:
    def wrapper(item: T) -> bool:
        return all(func(item) for func in funcs)

    return wrapper


def any_lazy(*funcs: Callable[[T], bool]) -> Callable[[T], bool]:
    def wrapper(item: T) -> bool:
        return any(func(item) for func in funcs)

    return wrapper


is_valid_canceled_order: Callable[[DetailedOrder], bool] = any_lazy(
    all_lazy(
        is_canceled_by_employee,
        partial(is_order_sales_channel,
                sales_channel=SalesChannel.DINE_IN),
    ),
    all_lazy(
        is_courier_assigned,
        partial(is_order_sales_channel,
                sales_channel=SalesChannel.DELIVERY),
    ),
)


def filter_valid_canceled_orders(
        orders: Iterable[DetailedOrder],
) -> list[DetailedOrder]:
    return [order for order in orders if is_valid_canceled_order(order)]
