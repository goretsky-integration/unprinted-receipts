import asyncio

import sentry_sdk
from fast_depends import Depends, inject

from config import Config, get_config
from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from connections.dodo_is import DodoIsConnection
from context.auth_credentials import AccountCookiesFetcher
from context.shifts import (
    ShiftsFetcher, ShiftDetailFetcher,
)
from dependencies import (
    get_auth_credentials_storage_connection,
    get_dodo_is_connection,
)
from logger import load_logging_config_from_file, setup_logging_config
from mappers import UnitsMapper, prepare_events
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
    units_mapper = UnitsMapper(units)
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

    accounts_cookies_fetch_result = await account_cookies_fetcher.fetch_all()

    account_name_to_cookies = {
        result.account_name: result.cookies
        for result in accounts_cookies_fetch_result.results
    }

    shifts_fetcher = ShiftsFetcher(dodo_is_connection)
    for account_name, cookies in account_name_to_cookies.items():
        unit_uuids = units_mapper.account_name_to_units[account_name].uuids
        shifts_fetcher.register_units(unit_uuids=unit_uuids, cookies=cookies)

    shifts = await shifts_fetcher.fetch_all()

    shift_detail_fetcher = ShiftDetailFetcher(dodo_is_connection)
    for shift in shifts.results:
        account_name = units_mapper.uuid_to_account_name[shift.unit_uuid]
        cookies = account_name_to_cookies[account_name]
        shift_detail_fetcher.register_shift(shift=shift, cookies=cookies)

    orders_fetch_result = await shift_detail_fetcher.fetch_all()

    events = prepare_events(
        unit_uuid_to_name=units_mapper.uuid_to_name,
        orders=orders_fetch_result.results,
    )

    await publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    # noinspection PyArgumentList
    asyncio.run(main())
