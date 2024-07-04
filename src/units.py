import pathlib
from typing import Final, TypeAlias

from pydantic import TypeAdapter

from models.units import Unit

__all__ = (
    'Units',
    'UNITS_FILE_PATH',
    'load_units_from_file',
)

Units: TypeAlias = tuple[Unit, ...]
UNITS_FILE_PATH: Final[pathlib.Path] = (
        pathlib.Path(__file__).parent.parent / 'accounts_units.json'
)


def load_units_from_file(file_path: pathlib.Path = UNITS_FILE_PATH) -> Units:
    accounts_units_json = file_path.read_text(encoding='utf-8')
    type_adapter = TypeAdapter(Units)
    return type_adapter.validate_json(accounts_units_json)
