import pytest

from factories import DetailedOrderFactory
from filters import is_canceled_by_employee


@pytest.mark.parametrize(
    'order',
    DetailedOrderFactory.create_batch(size=10)
)
def test_canceled_by_employee_orders(order):
    assert is_canceled_by_employee(order)


@pytest.mark.parametrize(
    'order',
    DetailedOrderFactory.create_batch(size=10, canceled_by_user_name=None)
)
def test_not_canceled_by_employee_orders(order):
    assert not is_canceled_by_employee(order)


if __name__ == '__main__':
    pytest.main()
