from datetime import datetime, timedelta

from fast_depends import Depends

from config import Config, get_config

__all__ = ('get_yesterday_this_moment',)


def get_yesterday_this_moment(config: Config = Depends(get_config)) -> datetime:
    return datetime.now(config.timezone) - timedelta(days=1)
