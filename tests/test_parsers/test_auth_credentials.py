import httpx
import pytest

from exceptions import AuthCredentialsParseError
from models import AccountCookies
from parsers.auth_credentials import (
    parse_account_cookies_response, parse_accounts_response,
)


@pytest.mark.parametrize(
    'content, expected',
    [
        (
                '[{"name": "account1"}, {"name": "account2"}]',
                {'account1', 'account2'},
        ),
        (
                '[]',
                set(),
        ),
    ],
)
def test_parse_accounts_response(content, expected):
    response = httpx.Response(200, content=content)
    assert parse_accounts_response(response) == expected


def test_parse_account_cookies_response():
    content = '''
    {"account_name": "account_1", "cookies": {"cookie1": "value1"}}
    '''
    response = httpx.Response(200, content=content)

    actual = parse_account_cookies_response(response, 'account_1')
    expected = AccountCookies(
        account_name='account_1',
        cookies={'cookie1': 'value1'},
    )
    assert actual == expected


def test_parse_account_cookies_response_invalid_json():
    response = httpx.Response(200, content='invalid json')
    with pytest.raises(AuthCredentialsParseError) as error:
        parse_account_cookies_response(response, 'account_1')

    assert error.value.account_name == 'account_1'
