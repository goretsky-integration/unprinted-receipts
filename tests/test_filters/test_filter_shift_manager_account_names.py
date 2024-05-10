from filters import filter_shift_manager_account_names


def test_filter_shift_manager_account_names():
    account_names = [
        'shift_manager_1',
        'shift_manager_2',
        'courier_1',
        'courier_2',
    ]
    assert filter_shift_manager_account_names(account_names) == {
        'shift_manager_1',
        'shift_manager_2',
    }


def test_filter_shift_manager_account_names_empty():
    account_names = []
    assert filter_shift_manager_account_names(account_names) == set()
