from collections.abc import Iterable
from datetime import datetime
from typing import Final, TypeAlias

import httpx
from bs4 import BeautifulSoup, Tag

from models import DetailedOrder, OrderHistoryItem, PartialOrder

__all__ = (
    'find_courier_name',
    'find_order_canceled_time',
    'find_order_created_time',
    'find_receipt_print_time',
    'find_canceled_by_user_name',
    'parse_order_history',
    'parse_detailed_order_response',
)

OrderHistoryItems: TypeAlias = Iterable[OrderHistoryItem]

CANCELED_ORDER_TITLES: Final[tuple[str, ...]] = (
    'has been rejected',
    'numaralı sipariş reddedildi',
)


def find_receipt_print_time(
        order_history_items: OrderHistoryItems,
) -> datetime | None:
    for item in order_history_items:
        if 'закрыт чек на возврат' in item.title.lower():
            return item.created_at


def find_order_created_time(
        order_history_items: OrderHistoryItems,
) -> datetime | None:
    for item in order_history_items:
        if 'has been accepted' in item.title.lower():
            return item.created_at


def find_order_canceled_time(
        order_history_items: OrderHistoryItems,
) -> datetime | None:
    for item in order_history_items:
        for title in CANCELED_ORDER_TITLES:
            if title in item.title.lower():
                return item.created_at


def find_canceled_by_user_name(
        order_history_items: OrderHistoryItems,
) -> str | None:
    for item in order_history_items:
        if item.user_name is None:
            continue

        for title in CANCELED_ORDER_TITLES:
            if title in item.title.lower():
                return item.user_name


def parse_order_history(rows: Iterable[Tag]) -> list[OrderHistoryItem]:
    order_history_items: list[OrderHistoryItem] = []
    for row in rows:
        columns = [column.text.strip() for column in row.find_all('td')]
        try:
            created_at, title, user_name = columns
        except ValueError:
            continue

        try:
            created_at = datetime.strptime(created_at, '%d.%m.%Y %H:%M:%S')
        except ValueError:
            continue

        user_name: str | None = user_name or None

        order_history_item = OrderHistoryItem(
            title=title,
            user_name=user_name,
            created_at=created_at,
        )
        order_history_items.append(order_history_item)

    return order_history_items


def find_courier_name(order_page: Tag) -> str | None:
    table: Tag | None = order_page.find('table')

    if table is None:
        return

    table_rows = table.find_all('tr')

    for row in table_rows:
        row_values = [field.text.strip() for field in row.find_all('td')]

        try:
            field_name, field_value = row_values
        except ValueError:
            continue

        field_value: str | None = field_value or None

        if field_name == 'Курьер:' and field_value is not None:
            return field_value


def parse_detailed_order_response(
        response: httpx.Response,
        partial_order: PartialOrder,
) -> DetailedOrder:
    soup = BeautifulSoup(response.text, 'lxml')

    # Department name is actually a unit name in shift manager's account
    unit_name = soup.find('div', class_='headerDepartment').text

    history_rows = soup.find('div', id='history').find_all('tr')[1:]

    order_history_items = parse_order_history(history_rows)

    courier_name = find_courier_name(soup)
    receipt_printed_at = find_receipt_print_time(order_history_items)
    order_created_at = find_order_created_time(order_history_items)
    order_canceled_at = find_order_canceled_time(order_history_items)
    rejected_by_user_name = find_canceled_by_user_name(order_history_items)

    return DetailedOrder(
        id=partial_order.id,
        price=partial_order.price,
        number=partial_order.number,
        sales_channel=partial_order.sales_channel,
        unit_name=unit_name,
        created_at=order_created_at,
        canceled_at=order_canceled_at,
        receipt_printed_at=receipt_printed_at,
        courier_name=courier_name,
        canceled_by_user_name=rejected_by_user_name,
    )
