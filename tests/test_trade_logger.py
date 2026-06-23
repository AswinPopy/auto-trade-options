import csv

from utils.trade_logger import TradeLogger


def test_log_trade_includes_daily_slope(tmp_path):
    logger = TradeLogger()
    logger.file = tmp_path / "trade_log.csv"
    logger.event_file = tmp_path / "trade_event_log.csv"

    logger._ensure_header()
    logger._ensure_event_header()

    logger.log_trade(
        order_id="123",
        symbol="BANKNIFTY",
        entry=100.0,
        entry_time="10:00",
        exit_price=105.0,
        qty=1,
        pnl=5.0,
        capital=100005.0,
        vwap=101.0,
        atr=0.5,
        strength=0.8,
        atr_ratio=1.2,
        volume_ratio=2.5,
        distance_from_vwap=0.3,
        daily_slope=1.25,
    )

    with logger.file.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert rows[0]["daily_slope"] == "1.25"
