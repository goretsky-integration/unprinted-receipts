from enum import StrEnum, auto

__all__ = ('CountryCode', 'SalesChannel')


class CountryCode(StrEnum):
    RU = auto()


class SalesChannel(StrEnum):
    DINE_IN = auto()
    TAKEAWAY = auto()
    DELIVERY = auto()
