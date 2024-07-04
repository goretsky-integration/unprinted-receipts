import httpx
from bs4 import BeautifulSoup, Tag

from models import OrderWithoutPrintedReceipt, ShiftPartialInfo

__all__ = (
    'ShiftPartialInfo',
    'OrderWithoutPrintedReceipt',
    'parse_shift_management_index_page',
    'parse_unprinted_receipts_page',
)


def parse_unprinted_receipts_page(
        response: httpx.Response,
) -> list[OrderWithoutPrintedReceipt]:
    soup = BeautifulSoup(response.text, 'lxml')

    unit_name_tag = soup.find('div', attrs={'class': 'headerDepartment'})

    if unit_name_tag is None:
        raise

    unit_name = unit_name_tag.text.strip()

    if ('В смене нет возвратов, незакрытых чеков и неоплаченных заказов'
            in soup.text):
        return []
    table_body = soup.find('tbody')

    if table_body is None:
        raise

    table_rows = table_body.find_all('tr')

    orders_without_printed_receipts: list[OrderWithoutPrintedReceipt] = []

    for table_row in table_rows:
        _, order_number_td, order_price_td, _, _ = table_row.find_all('td')

        order_number_td: Tag
        order_price_td: Tag

        order_number = order_number_td.text.strip()
        order_price = order_price_td.text.strip().replace(' ', '')

        orders_without_printed_receipts.append(
            OrderWithoutPrintedReceipt(
                unit_name=unit_name,
                number=order_number,
                price=int(order_price),
            ),
        )

    return orders_without_printed_receipts


def parse_shift_management_index_page(
        response: httpx.Response,
        unit_name: str,
) -> list[ShiftPartialInfo]:
    soup = BeautifulSoup(response.text, 'lxml')

    a_tags = soup.find_all('a')

    shift_partials: list[ShiftPartialInfo] = []

    for a_tag in a_tags:

        href: str = a_tag.get('href', '')

        if '/Managment/ShiftManagment/ZReport' not in href:
            continue

        _, query_params = href.split('?')

        query_params: str

        cash_box_id = shift_id = None

        for query_param in query_params.split('&'):
            query_param_key, query_param_value = query_param.split('=')

            if query_param_key == 'cashBoxId':
                cash_box_id = query_param_value

            if query_param_key == 'shiftId':
                shift_id = query_param_value

        if not all((cash_box_id, shift_id)):
            continue

        shift_partials.append(
            ShiftPartialInfo(
                unit_name=unit_name,
                cash_box_id=cash_box_id,
                shift_id=shift_id,
            ),
        )

    return shift_partials
