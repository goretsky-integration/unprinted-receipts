import pytest

from connections.helpers import retry_on_failure


@pytest.mark.asyncio
async def test_retry_on_failure_success_on_last_attempt():
    called = failed = 0

    @retry_on_failure(attempts=5)
    async def func():
        nonlocal called, failed
        called += 1
        if failed < 4:
            failed += 1
            raise Exception('Test error')

    await func()

    assert failed == 4
    assert called == failed + 1


@pytest.mark.asyncio
async def test_retry_on_failure_success_on_first_attempt():
    called = 0

    @retry_on_failure(attempts=5)
    async def func():
        nonlocal called
        called += 1

    await func()

    assert called == 1


@pytest.mark.parametrize('attempts', [1, 2, 3, 4, 5])
@pytest.mark.asyncio
async def test_retry_on_failure_fail_all(attempts: int):
    called = failed = 0

    @retry_on_failure(attempts=attempts)
    async def func():
        nonlocal called, failed
        called += 1
        if failed < attempts:
            failed += 1
            raise Exception('Test error')

    with pytest.raises(Exception) as error:
        await func()

    assert error.value.args[0] == (
        f'Failed to execute "{func.__name__}"'
        f' after {attempts} attempts'
    )

    assert failed == attempts
    assert called == failed


@pytest.mark.parametrize(
    'attempts',
    [0, -1, -100],
)
def test_retry_on_failure_attempts_lower_than_1(attempts):
    with pytest.raises(ValueError) as error:
        @retry_on_failure(attempts=attempts)
        async def func():
            pass

    assert error.value.args[0] == f'Attempts must be greater than 0'


def test_retry_on_failure_sync_function_passed():
    with pytest.raises(ValueError) as error:
        @retry_on_failure(attempts=5)
        def func():
            pass

    assert error.value.args[0] == 'Function must be async'
