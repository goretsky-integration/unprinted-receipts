from pydantic import BaseModel, Field

from enums import CountryCode
from models import DetailedOrder

__all__ = ('EventPayload', 'Event')


class EventPayload(BaseModel):
    unit_name: str
    orders: list[DetailedOrder]
    country_code: CountryCode


class Event(BaseModel):
    unit_ids: list[int]
    type: str = Field(default='CANCELED_ORDERS', frozen=True)
    payload: EventPayload
