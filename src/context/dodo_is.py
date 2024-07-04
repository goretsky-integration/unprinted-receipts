import asyncio
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TypeAlias, TypeVar

from connections.dodo_is import DodoIsConnection
from exceptions import ApplicationError, UnprintedReceiptsPageParseError
from parsers.shift_management import (
    OrderWithoutPrintedReceipt,
    ShiftPartialInfo,
    parse_shift_management_index_page,
    parse_unprinted_receipts_page,
)

__all__ = (
    'ShiftsPartialInfoFetcher',
    'OrdersWithoutPrintedReceiptsFetcher',
)

UnitNamesAndCookies: TypeAlias = list[tuple[str, Mapping[str, str]]]

T = TypeVar('T')


def flatten(list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    return [item for sublist in list_of_lists for item in sublist]


@dataclass(frozen=True, slots=True)
class UnprintedReceiptsFetchResult:
    unit_name: str
    result: list[OrderWithoutPrintedReceipt] | None = None
    exception: ApplicationError | None = None


@dataclass(frozen=True, slots=True)
class UnprintedReceiptsFetchAllResult:
    results: list[OrderWithoutPrintedReceipt]
    errors: list[ApplicationError]


class ShiftsPartialInfoFetcher:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__connection = dodo_is_connection
        self.__unit_names_and_cookies_registry: UnitNamesAndCookies = []

    def register_unit(self, unit_name: str, cookies: Mapping[str, str]) -> None:
        self.__unit_names_and_cookies_registry.append((unit_name, cookies))

    async def fetch_unit(
            self,
            unit_name: str,
            cookies: Mapping[str, str],
    ) -> list[ShiftPartialInfo]:
        response = await self.__connection.get_shift_management_partial_index(
            cookies=cookies,
            unit_name=unit_name,
        )
        return parse_shift_management_index_page(
            response=response,
            unit_name=unit_name,
        )

    async def fetch_all(self) -> list[ShiftPartialInfo]:
        tasks: list[asyncio.Task] = []
        async with asyncio.TaskGroup() as task_group:
            for unit_name, cookies in self.__unit_names_and_cookies_registry:
                tasks.append(
                    task_group.create_task(
                        self.fetch_unit(
                            unit_name=unit_name,
                            cookies=cookies,
                        )
                    )
                )

        results = [task.result() for task in tasks]
        return flatten(results)


class OrdersWithoutPrintedReceiptsFetcher:

    def __init__(self, dodo_is_connection: DodoIsConnection):
        self.__connection = dodo_is_connection
        self.__shifts_partial_info_and_cookies_registry = []

    def register_unit(
            self,
            shift_partial_info: ShiftPartialInfo,
            cookies: Mapping[str, str],
    ) -> None:
        self.__shifts_partial_info_and_cookies_registry.append(
            (shift_partial_info, cookies),
        )

    async def fetch_unit(
            self,
            shift_partial_info: ShiftPartialInfo,
            cookies: Mapping[str, str],
    ) -> UnprintedReceiptsFetchResult:
        response = await self.__connection.get_unprinted_receipts(
            cookies=cookies,
            shift_id=shift_partial_info.shift_id,
            cash_box_id=shift_partial_info.cash_box_id,
            unit_name=shift_partial_info.unit_name,
        )

        try:
            result = parse_unprinted_receipts_page(
                response=response,
                unit_name=shift_partial_info.unit_name,
            )
        except UnprintedReceiptsPageParseError as error:
            return UnprintedReceiptsFetchResult(
                unit_name=shift_partial_info.unit_name,
                exception=error,
            )
        return UnprintedReceiptsFetchResult(
            unit_name=shift_partial_info.unit_name,
            result=result,
        )

    async def fetch_all(self) -> UnprintedReceiptsFetchAllResult:
        tasks: list[asyncio.Task[UnprintedReceiptsFetchResult]] = []

        async with asyncio.TaskGroup() as task_group:
            for shift_partial_info, cookies in (
                    self.__shifts_partial_info_and_cookies_registry
            ):
                tasks.append(
                    task_group.create_task(
                        self.fetch_unit(
                            shift_partial_info=shift_partial_info,
                            cookies=cookies,
                        )
                    )
                )

        results: list[OrderWithoutPrintedReceipt] = []
        errors: list[ApplicationError] = []

        for task in tasks:
            result = task.result()

            if result.exception is not None:
                errors.append(result.exception)
            else:
                results += result.result

        return UnprintedReceiptsFetchAllResult(
            results=results,
            errors=errors,
        )



        return [task.result() for task in tasks]
