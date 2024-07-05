import httpx
from bs4 import BeautifulSoup, Tag

from exceptions import UnprintedReceiptsPageParseError
from models import OrderWithoutPrintedReceipt, ShiftPartialInfo

__all__ = (
    'ShiftPartialInfo',
    'OrderWithoutPrintedReceipt',
    'parse_shift_management_index_page',
    'parse_unprinted_receipts_page',
)


def parse_unprinted_receipts_page(
        response: httpx.Response,
        unit_name: str,
) -> list[OrderWithoutPrintedReceipt]:
    soup = BeautifulSoup(response.text, 'lxml')

    unit_name_tag = soup.find('div', attrs={'class': 'headerDepartment'})

    if unit_name_tag is None:
        raise UnprintedReceiptsPageParseError(
            unit_name=unit_name,
            response_body=response.text,
        )

    unit_name = unit_name_tag.text.strip()

    if ('В смене нет возвратов, незакрытых чеков и неоплаченных заказов'
            in soup.text):
        return []

    table_rows = soup.find_all('tr')

    if not table_rows:
        raise UnprintedReceiptsPageParseError(
            unit_name=unit_name,
            response_body=response.text,
        )

    orders_without_printed_receipts: list[OrderWithoutPrintedReceipt] = []

    for table_row in table_rows[1:]:
        tds = table_row.find_all('td')

        if len(tds) != 5:
            continue

        _, order_number_td, order_price_td, _, _ = table_row.find_all('td')

        order_number_td: Tag
        order_price_td: Tag

        order_number = order_number_td.text.strip()
        order_price = order_price_td.text.strip().replace(' ', '')

        orders_without_printed_receipts.append(
            OrderWithoutPrintedReceipt(
                unit_name=unit_name,
                number=order_number,
                price=int(order_price.replace('\xa0i', '')
                          .replace('\xa0', '')),
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

    all_query_params: set[str] = set()

    for a_tag in a_tags:

        href: str = a_tag.get('href', '')

        if '/Managment/ShiftManagment/ZReport' not in href:
            continue

        _, query_params = href.split('?')
        all_query_params.add(query_params)

    for query_params in all_query_params:
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
