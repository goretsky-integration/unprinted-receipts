import pytest

from enums import SalesChannel
from factories import DetailedOrderFactory
from filters import is_order_sales_channel


@pytest.mark.parametrize(
    'order',
    [
        DetailedOrderFactory(sales_channel=SalesChannel.DINE_IN),
        DetailedOrderFactory(sales_channel=SalesChannel.TAKEAWAY),
        DetailedOrderFactory(sales_channel=SalesChannel.DELIVERY),
    ],
)
def test_order_sales_channel(order):
    assert is_order_sales_channel(order, order.sales_channel)


@pytest.mark.parametrize(
    'order, sales_channel',
    [
        (
                DetailedOrderFactory(sales_channel=SalesChannel.DINE_IN),
                SalesChannel.TAKEAWAY,
        ),
        (
                DetailedOrderFactory(sales_channel=SalesChannel.DINE_IN),
                SalesChannel.DELIVERY,
        ),
        (
                DetailedOrderFactory(sales_channel=SalesChannel.TAKEAWAY),
                SalesChannel.DINE_IN,
        ),
        (
                DetailedOrderFactory(sales_channel=SalesChannel.TAKEAWAY),
                SalesChannel.DELIVERY,
        ),
        (
                DetailedOrderFactory(sales_channel=SalesChannel.DELIVERY),
                SalesChannel.TAKEAWAY,
        ),
        (
                DetailedOrderFactory(sales_channel=SalesChannel.DELIVERY),
                SalesChannel.DINE_IN,
        ),
    ],
)
def test_order_not_sales_channel(order, sales_channel):
    assert not is_order_sales_channel(order, sales_channel)


if __name__ == '__main__':
    pytest.main()
