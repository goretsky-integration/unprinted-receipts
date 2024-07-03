import pathlib
from typing import Final, TypeAlias

from pydantic import TypeAdapter

from models.units import AccountUnits

__all__ = (
    'ACCOUNTS_UNITS_FILE_PATH',
    'load_accounts_units_from_file',
    'AccountsUnits',
)

AccountsUnits: TypeAlias = tuple[AccountUnits, ...]

ACCOUNTS_UNITS_FILE_PATH: Final[pathlib.Path] = (
        pathlib.Path(__file__).parent.parent / 'accounts_units.json'
)


def load_accounts_units_from_file(
        file_path: pathlib.Path = ACCOUNTS_UNITS_FILE_PATH
) -> AccountsUnits:
    accounts_units_json = file_path.read_text(encoding='utf-8')
    type_adapter = TypeAdapter(AccountsUnits)
    return type_adapter.validate_json(accounts_units_json)
