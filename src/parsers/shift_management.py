import traceback
from uuid import UUID

import httpx
from pydantic import TypeAdapter, ValidationError

from exceptions import APIResponseParseError
from models import Order, Shift

__all__ = (
    'parse_shifts_response',
    'parse_shift_response',
)


def parse_shifts_response(
        response: httpx.Response,
        unit_uuid: UUID,
) -> list[Shift]:
    response_data = response.json()

    try:
        shifts = response_data['Shifts']
    except KeyError:
        raise APIResponseParseError(
            message='missing "Shifts" object',
            response=response,
        )

    if not isinstance(shifts, list):
        raise APIResponseParseError(
            message='"Shifts" field is not a list',
            response=response,
        )

    shifts = [shift | {'unit_uuid': unit_uuid} for shift in shifts]

    type_adapter = TypeAdapter(list[Shift])

    try:
        return type_adapter.validate_python(shifts)
    except ValidationError:
        raise APIResponseParseError(
            message='failed to validate "Shift" objects',
            response=response,
        )


def parse_shift_response(
        response: httpx.Response,
        unit_uuid: UUID,
) -> list[Order]:
    response_data = response.json()

    try:
        orders_statistics = response_data['OrdersStatistic']
    except KeyError:
        raise APIResponseParseError(
            message='missing "OrdersStatistic" object',
            response=response,
        )

    if not isinstance(orders_statistics, dict):
        raise APIResponseParseError(
            message='"OrdersStatistic" field is not an object',
            response=response,
        )

    try:
        prepaid_orders_statistics = orders_statistics['Prepaid']
    except KeyError:
        raise APIResponseParseError(
            message='missing "Prepaid" object',
            response=response,
        )

    if not isinstance(prepaid_orders_statistics, dict):
        raise APIResponseParseError(
            message='"Prepaid" field is not an object',
            response=response,
        )

    orders: list[Order] = []
    type_adapter = TypeAdapter(list[Order])

    for cash_box in prepaid_orders_statistics['Items']:
        items = [item | {'unit_uuid': unit_uuid} for item in cash_box['Items']]
        try:
            orders += type_adapter.validate_python(items)
        except ValidationError:
            raise APIResponseParseError(
                message='failed to validate "Order" objects',
                response=response,
            )

    return orders
