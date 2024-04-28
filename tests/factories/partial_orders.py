import factory

from enums import SalesChannel
from models import PartialOrder

__all__ = ('PartialOrderFactory',)


class PartialOrderFactory(factory.Factory):
    class Meta:
        model = PartialOrder

    id = factory.Faker('uuid4')
    price = factory.Faker('pyint', min_value=1, max_value=100)
    number = factory.Sequence(lambda n: f'{n}-0')
    sales_channel = factory.Faker(
        'random_element',
        elements=SalesChannel,
    )
