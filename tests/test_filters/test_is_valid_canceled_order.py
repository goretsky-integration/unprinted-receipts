import pytest

from enums import SalesChannel
from factories import DetailedOrderFactory
from filters import is_valid_canceled_order


@pytest.mark.parametrize(
    'order',
    [
        DetailedOrderFactory(sales_channel=SalesChannel.DINE_IN),
        DetailedOrderFactory(sales_channel=SalesChannel.DELIVERY),
    ],
)
def test_valid_canceled_orders(order):
    assert is_valid_canceled_order(order)


@pytest.mark.parametrize(
    'order',
    [
        DetailedOrderFactory(
            sales_channel=SalesChannel.DELIVERY,
            courier_name=None,
        ),
        DetailedOrderFactory(
            sales_channel=SalesChannel.DINE_IN,
            canceled_by_user_name=None,
        ),
    ],
)
def test_invalid_canceled_order(order):
    assert not is_valid_canceled_order(order)


if __name__ == '__main__':
    pytest.main()
