import httpx
from pydantic import TypeAdapter

from models import Unit

__all__ = ('parse_units_response',)


def parse_units_response(response: httpx.Response) -> list[Unit]:
    type_adapter = TypeAdapter(list[Unit])
    response_data: dict = response.json()
    return type_adapter.validate_python(response_data['units'])
