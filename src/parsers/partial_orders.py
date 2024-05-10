import httpx
from bs4 import BeautifulSoup

from enums import SalesChannel
from models import PartialOrder

__all__ = ('parse_partial_orders_response',)


def parse_partial_orders_response(
        response: httpx.Response,
        account_name: str,
) -> list[PartialOrder]:
    soup = BeautifulSoup(response.text, 'lxml')

    rows = soup.find_all('tr')[1:]

    sales_channel_map: dict[str, SalesChannel] = {
        'Доставка': SalesChannel.DELIVERY,
        'Самовывоз': SalesChannel.TAKEAWAY,
        'Ресторан': SalesChannel.DINE_IN,
    }

    partial_orders: list[PartialOrder] = []

    for row in rows:
        columns = row.find_all('td')

        order_id = columns[0].find('a')['href'].split('=')[-1]
        order_number = columns[1].text.strip()
        order_price = columns[4].text.removesuffix(' ₽')
        sales_channel = sales_channel_map[columns[7].text]

        order = PartialOrder(
            id=order_id,
            number=order_number,
            price=order_price,
            sales_channel=sales_channel,
            account_name=account_name,
        )
        partial_orders.append(order)

    return partial_orders
