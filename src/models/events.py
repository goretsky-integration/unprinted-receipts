from uuid import UUID

from pydantic import BaseModel, Field, conlist

from models.dodo_is import OrderWithoutPrintedReceipt

__all__ = ('EventPayload', 'Event')


class EventPayload(BaseModel):
    unit_name: str
    orders: conlist(OrderWithoutPrintedReceipt, min_length=1)


class Event(BaseModel):
    unit_ids: UUID
    type: str = Field(default='UNPRINTED_RECEIPTS', frozen=True)
    payload: EventPayload
