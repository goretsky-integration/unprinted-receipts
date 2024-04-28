import pytest

from factories import DetailedOrderFactory
from filters import is_courier_assigned


@pytest.mark.parametrize(
    'order',
    DetailedOrderFactory.create_batch(size=10),
)
def test_courier_assigned_orders(order):
    assert is_courier_assigned(order)


@pytest.mark.parametrize(
    'order',
    DetailedOrderFactory.create_batch(size=10, courier_name=None),
)
def test_courier_not_assigned_orders(order):
    assert not is_courier_assigned(order)


if __name__ == '__main__':
    pytest.main()
