from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar

from connections.dodo_is import DodoIsConnection
from exceptions import (
    ApplicationError, UnexpectedError,
    UnprintedReceiptsPageParseError,
)
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

from tasks_executor import execute_batched_tasks

UnitNamesAndCookies: TypeAlias = list[tuple[str, Mapping[str, str]]]

T = TypeVar('T')


def flatten(list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    return [item for sublist in list_of_lists for item in sublist]


@dataclass(frozen=True, slots=True, kw_only=True)
class FetchResult(Generic[T]):
    unit_name: str
    result: list[T] | None = None
    exception: ApplicationError | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class FetchAllResult(Generic[T]):
    results: list[T]
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

    async def try_fetch_unit(
            self,
            unit_name: str,
            cookies: Mapping[str, str],
    ) -> FetchResult[ShiftPartialInfo]:
        try:
            shifts_partial_info = await self.fetch_unit(
                unit_name=unit_name,
                cookies=cookies,
            )
        except ApplicationError as error:
            return FetchResult(
                unit_name=unit_name,
                exception=error,
            )
        except Exception as error:
            return FetchResult(
                unit_name=unit_name,
                exception=UnexpectedError(exception=error),
            )
        return FetchResult(
            unit_name=unit_name,
            result=shifts_partial_info,
        )

    async def fetch_all(self) -> FetchAllResult[ShiftPartialInfo]:
        coroutines = [
            self.try_fetch_unit(
                unit_name=unit_name,
                cookies=cookies,
            )
            for unit_name, cookies in
            self.__unit_names_and_cookies_registry
        ]

        results: list[ShiftPartialInfo] = []
        errors: list[ApplicationError] = []

        async for tasks in execute_batched_tasks(coroutines, batch_size=10):
            for task in tasks:
                result = task.result()
                if result.exception is not None:
                    errors.append(result.exception)
                else:
                    results += result.result

        return FetchAllResult(results=results, errors=errors)


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
    ) -> list[OrderWithoutPrintedReceipt]:
        response = await self.__connection.get_unprinted_receipts(
            cookies=cookies,
            shift_id=shift_partial_info.shift_id,
            cash_box_id=shift_partial_info.cash_box_id,
            unit_name=shift_partial_info.unit_name,
        )
        return parse_unprinted_receipts_page(
            response=response,
            unit_name=shift_partial_info.unit_name,
        )

    async def try_fetch_unit(
            self,
            shift_partial_info: ShiftPartialInfo,
            cookies: Mapping[str, str],
    ) -> FetchResult[OrderWithoutPrintedReceipt]:
        try:
            result = await self.fetch_unit(
                shift_partial_info=shift_partial_info,
                cookies=cookies
            )
        except UnprintedReceiptsPageParseError as error:
            return FetchResult(
                unit_name=shift_partial_info.unit_name,
                exception=error,
            )
        return FetchResult(
            unit_name=shift_partial_info.unit_name,
            result=result,
        )

    async def fetch_all(self) -> FetchAllResult[OrderWithoutPrintedReceipt]:
        coroutines = [
            self.try_fetch_unit(
                shift_partial_info=shift_partial_info,
                cookies=cookies,
            )
            for shift_partial_info, cookies in
            self.__shifts_partial_info_and_cookies_registry
        ]

        results: list[OrderWithoutPrintedReceipt] = []
        errors: list[ApplicationError] = []

        async for tasks in execute_batched_tasks(coroutines, batch_size=10):

            for task in tasks:
                result = task.result()

                if result.exception is not None:
                    errors.append(result.exception)
                else:
                    results += result.result

        return FetchAllResult(
            results=results,
            errors=errors,
        )
