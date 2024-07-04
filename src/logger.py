import json
import logging.config
import pathlib
from typing import Any, Final

__all__ = (
    'create_logger',
    'setup_logging_config',
    'load_logging_config_from_file',
    'LOGGING_CONFIG_FILE_PATH',
)

LOGGING_CONFIG_FILE_PATH: Final[pathlib.Path] = (
        pathlib.Path(__file__).parent.parent / 'logging_config.json'
)


def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    return logger


def setup_logging_config(logging_config: dict[str, Any]) -> None:
    logging.config.dictConfig(logging_config)


def load_logging_config_from_file(
        file_path: pathlib.Path = LOGGING_CONFIG_FILE_PATH,
) -> dict[str, Any]:
    config_json = file_path.read_text(encoding='utf-8')
    return json.loads(config_json)
