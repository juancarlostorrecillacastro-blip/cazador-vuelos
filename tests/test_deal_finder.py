from flight_hunter.deal_finder import is_new_best_price


def test_is_new_best_price_when_no_previous_record():
    assert is_new_best_price(32, None) is True


def test_is_new_best_price_when_price_dropped():
    assert is_new_best_price(25, 32) is True


def test_is_new_best_price_when_price_did_not_improve():
    assert is_new_best_price(32, 32) is False
    assert is_new_best_price(40, 32) is False
