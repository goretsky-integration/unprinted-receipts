from factories.detailed_orders import DetailedOrderFactory


def test_detailed_order_has_no_printed_receipt():
    detailed_order = DetailedOrderFactory(receipt_printed_at=None)
    assert not detailed_order.has_printed_receipt


def test_detailed_order_has_printed_receipt():
    detailed_order = DetailedOrderFactory()
    assert detailed_order.has_printed_receipt
