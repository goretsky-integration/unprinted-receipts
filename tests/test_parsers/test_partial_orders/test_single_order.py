import pathlib
from uuid import UUID

import httpx

from enums import SalesChannel
from models import PartialOrder
from parsers import parse_partial_orders_response


def test_no_partial_orders():
    file_path = pathlib.Path(__file__).parent / "single_order.html"
    html = file_path.read_text(encoding='utf-8')
    response = httpx.Response(200, content=html)

    actual = parse_partial_orders_response(response, 'account1')
    expected = [
        PartialOrder(
            id=UUID('72306462-5357-a1e0-11ef-0dfdb02da68a'),
            price=330,
            number='174 - 1',
            sales_channel=SalesChannel.DINE_IN,
            account_name='account1',
        ),
    ]

    assert actual == expected
