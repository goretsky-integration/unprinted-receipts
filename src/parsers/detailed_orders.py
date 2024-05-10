import itertools
from collections.abc import Iterable
from datetime import datetime
from functools import cached_property
from typing import Final, TypeAlias

import httpx
from bs4 import BeautifulSoup, Tag
import structlog.stdlib
from pydantic import ValidationError

from exceptions import DetailedOrderParseError
from models import DetailedOrder, OrderHistoryItem, PartialOrder

__all__ = ('DetailedOrderParser',)

logger = structlog.stdlib.get_logger('parser')

OrderHistoryItems: TypeAlias = Iterable[OrderHistoryItem]


class DetailedOrderParser:
    canceled_order_titles: Final[tuple[str, ...]] = (
        'has been rejected',
        'numaralı sipariş reddedildi',
        'rezygnacja z zamówienia',
    )

    def __init__(self, response: httpx.Response, partial_order: PartialOrder):
        self.__response = response
        self.__partial_order = partial_order
        self.__order_page = BeautifulSoup(self.__response.text, 'lxml')

    @cached_property
    def history_rows(self) -> list[Tag]:
        history = self.__order_page.find('div', id='history')
        if history is None:
            raise DetailedOrderParseError(order_id=self.__partial_order.id)
        return history.find_all('tr')[1:]

    @cached_property
    def order_history_items_with_user_name(
            self,
    ) -> list[OrderHistoryItem]:
        return [
            item for item in self.order_history_items
            if item.user_name is not None
        ]

    @cached_property
    def order_history_items(self) -> list[OrderHistoryItem]:
        order_history_items: list[OrderHistoryItem] = []
        for row in self.history_rows:
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
                title=title.lower(),
                user_name=user_name,
                created_at=created_at,
            )
            order_history_items.append(order_history_item)

        return order_history_items

    def iter_canceled_order_titles_and_order_history_items(
            self,
            order_history_items: Iterable[OrderHistoryItem],
    ) -> itertools.product[tuple[str, OrderHistoryItem]]:
        return itertools.product(
            self.canceled_order_titles,
            order_history_items,
        )

    def find_order_canceled_time(self) -> datetime | None:
        iterator = self.iter_canceled_order_titles_and_order_history_items(
            order_history_items=self.order_history_items,
        )
        for canceled_order_title, order_history_item in iterator:
            if canceled_order_title in order_history_item.title:
                return order_history_item.created_at

    def find_canceled_by_user_name(self) -> str | None:
        iterator = self.iter_canceled_order_titles_and_order_history_items(
            order_history_items=self.order_history_items_with_user_name,
        )
        for canceled_order_title, order_history_item in iterator:
            if canceled_order_title in order_history_item.title:
                return order_history_item.user_name

    def find_receipt_print_time(self) -> datetime | None:
        for item in self.order_history_items:
            if 'закрыт чек на возврат' in item.title:
                return item.created_at

    def find_order_created_time(self) -> datetime | None:
        for item in self.order_history_items:
            if 'has been accepted' in item.title:
                return item.created_at

    def find_courier_name(self) -> str | None:
        table: Tag | None = self.__order_page.find('table')
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

    def find_unit_name(self) -> str | None:
        """
        Find unit name in order page HTML.
        Department name is actually a unit name in shift manager's account.

        Args:
            order_page: bs4.Tag object.

        Returns:
            Unit name or None.
        """
        unit_name_tag = self.__order_page.find('div', class_='headerDepartment')
        return unit_name_tag.text.strip() if unit_name_tag else None

    def parse(self) -> DetailedOrder:
        """
        Parse detailed order page HTML.

        Returns:
            DetailedOrder object.

        Raises:
            DetailedOrderParseError: Parsing error.
        """
        unit_name = self.find_unit_name()
        courier_name = self.find_courier_name()
        receipt_printed_at = self.find_receipt_print_time()
        order_created_at = self.find_order_created_time()
        order_canceled_at = self.find_order_canceled_time()
        rejected_by_user_name = self.find_canceled_by_user_name()

        try:
            return DetailedOrder(
                id=self.__partial_order.id,
                price=self.__partial_order.price,
                number=self.__partial_order.number,
                sales_channel=self.__partial_order.sales_channel,
                unit_name=unit_name,
                created_at=order_created_at,
                canceled_at=order_canceled_at,
                receipt_printed_at=receipt_printed_at,
                courier_name=courier_name,
                canceled_by_user_name=rejected_by_user_name,
            )
        except ValidationError as error:
            logger.error(
                'Could not parse detailed order: validation error',
                order_id=str(self.__partial_order.id),
            )
            raise DetailedOrderParseError(
                order_id=self.__partial_order.id,
            ) from error
