from automation.engine import _money, _recommend


def test_money_parser() -> None:
    assert _money("₦389,000") == 389000


def test_critical_gap() -> None:
    severity, _, _, opportunity = _recommend(449000, 389000, "in")
    assert severity == "CRITICAL"
    assert opportunity > 0


def test_out_of_stock_protects_margin() -> None:
    severity, message, _, opportunity = _recommend(189000, 198000, "out")
    assert severity == "LOW"
    assert opportunity == 0
    assert "margin" in message.lower()
