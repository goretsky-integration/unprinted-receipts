from pydantic import BaseModel

__all__ = ('ShiftPartialInfo', 'OrderWithoutPrintedReceipt')


class ShiftPartialInfo(BaseModel):
    unit_name: str
    cash_box_id: int
    shift_id: int


class OrderWithoutPrintedReceipt(BaseModel):
    unit_name: str
    number: str
    price: int
