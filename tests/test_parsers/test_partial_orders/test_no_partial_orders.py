import pathlib

import httpx

from parsers import parse_partial_orders_response


def test_no_partial_orders():
    file_path = pathlib.Path(__file__).parent / "no_orders.html"
    html = file_path.read_text(encoding='utf-8')
    response = httpx.Response(200, content=html)

    actual = parse_partial_orders_response(response, 'account1')
    expected = []

    assert actual == expected
