from uuid import UUID

import httpx

from models import Unit
from parsers.units import parse_units_response


def test_parse_units():
    content = '''
    {
        "units": [
            {
                "id": 1,
                "name": "Moscow 1-1",
                "uuid": "e8b0950f-2246-4fa4-80cb-2c0b8c19176a"
            }
        ]
    }
    '''
    response = httpx.Response(200, content=content)

    units = parse_units_response(response)

    assert units == [
        Unit(
            id=1,
            name='Moscow 1-1',
            uuid=UUID('e8b0950f-2246-4fa4-80cb-2c0b8c19176a'),
        ),
    ]
