import asyncio

import sentry_sdk
from fast_depends import Depends, inject

from config import Config, get_config
from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from connections.dodo_is import DodoIsConnection
from context.auth_credentials import AccountCookiesFetcher
from context.dodo_is import (
    OrdersWithoutPrintedReceiptsFetcher,
    ShiftsPartialInfoFetcher,
)
from dependencies import (
    get_auth_credentials_storage_connection,
    get_dodo_is_connection,
)
from logger import load_logging_config_from_file, setup_logging_config
from mappers import prepare_events
from message_queue import publish_events
from units import Units, load_units_from_file


@inject
async def main(
        auth_credentials_connection: AuthCredentialsStorageConnection = Depends(
            get_auth_credentials_storage_connection,
        ),
        dodo_is_connection: DodoIsConnection = Depends(
            get_dodo_is_connection,
        ),
        units: Units = Depends(load_units_from_file),
        config: Config = Depends(get_config),
        logging_config: dict = Depends(load_logging_config_from_file),
):
    if config.sentry.is_enabled:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
        )

    setup_logging_config(logging_config)

    account_cookies_fetcher = AccountCookiesFetcher(
        connection=auth_credentials_connection,
    )
    for unit in units:
        account_cookies_fetcher.register_account_name(unit.account_name)

    account_name_to_unit_name = {
        unit.account_name: unit.name for unit in units
    }
    unit_name_to_account_name = {
        unit.name: unit.account_name for unit in units
    }

    accounts_cookies_fetch_result = await account_cookies_fetcher.fetch_all()

    account_name_to_cookies = {
        result.account_name: result.cookies
        for result in accounts_cookies_fetch_result.results
    }

    shifts_partial_info_fetcher = ShiftsPartialInfoFetcher(dodo_is_connection)
    for result in accounts_cookies_fetch_result.results:
        shifts_partial_info_fetcher.register_unit(
            unit_name=account_name_to_unit_name[result.account_name],
            cookies=result.cookies,
        )

    shifts_partial_info_fetch_result = (
        await shifts_partial_info_fetcher.fetch_all()
    )

    orders_without_printed_receipts_fetcher = (
        OrdersWithoutPrintedReceiptsFetcher(dodo_is_connection)
    )
    for shift_partial_info in shifts_partial_info_fetch_result.results:
        account_name = unit_name_to_account_name[shift_partial_info.unit_name]
        cookies = account_name_to_cookies[account_name]

        orders_without_printed_receipts_fetcher.register_unit(
            shift_partial_info=shift_partial_info,
            cookies=cookies,
        )

    orders_without_printed_receipts_fetch_result = (
        await orders_without_printed_receipts_fetcher.fetch_all()
    )

    events = prepare_events(
        unit_name_to_uuid={unit.name: unit.uuid for unit in units},
        orders=orders_without_printed_receipts_fetch_result.results,
    )

    await publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    # noinspection PyArgumentList
    asyncio.run(main())
