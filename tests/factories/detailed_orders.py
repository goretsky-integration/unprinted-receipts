import factory

from factories.partial_orders import PartialOrderFactory
from models import DetailedOrder

__all__ = ('DetailedOrderFactory',)


class DetailedOrderFactory(PartialOrderFactory):
    class Meta:
        model = DetailedOrder

    unit_name = factory.Faker('word')
    created_at = factory.Faker('date_time')
    canceled_at = factory.Faker('date_time')
    receipt_printed_at = factory.Faker('date_time')
    courier_name = factory.Faker('name')
    canceled_by_user_name = factory.Faker('name')
