from datetime import datetime

from data.candle_engine import CandleEngine
from strategy.slope_filter import calculate_daily_slope, should_allow_trade


def test_buy_ce_is_allowed_only_with_positive_slope():
    positive_slope_candles = [
        {"open": 100.0, "close": 105.0},
        {"open": 105.0, "close": 115.0},
        {"open": 115.0, "close": 120.0},
    ]
    negative_slope_candles = [
        {"open": 100.0, "close": 95.0},
        {"open": 95.0, "close": 90.0},
        {"open": 90.0, "close": 85.0},
    ]

    assert calculate_daily_slope(positive_slope_candles) > 0
    assert should_allow_trade("BUY_CE", positive_slope_candles) is True
    assert should_allow_trade("BUY_CE", negative_slope_candles) is False


def test_buy_pe_is_allowed_only_with_negative_slope():
    positive_slope_candles = [
        {"open": 100.0, "close": 105.0},
        {"open": 105.0, "close": 115.0},
        {"open": 115.0, "close": 120.0},
    ]
    negative_slope_candles = [
        {"open": 100.0, "close": 95.0},
        {"open": 95.0, "close": 90.0},
        {"open": 90.0, "close": 85.0},
    ]

    assert calculate_daily_slope(negative_slope_candles) < 0
    assert should_allow_trade("BUY_PE", negative_slope_candles) is True
    assert should_allow_trade("BUY_PE", positive_slope_candles) is False


def test_day_candles_includes_full_day_history():
    engine = CandleEngine()
    today = datetime.now().date()

    engine.history["TEST"] = [
        {"date": today, "open": 100.0, "close": 102.0},
        {"date": today, "open": 102.0, "close": 104.0},
    ]
    engine.current["TEST"] = {
        "date": today,
        "open": 104.0,
        "close": 106.0,
    }

    candles = engine.get_day_candles("TEST")

    assert len(candles) == 3
    assert candles[0]["open"] == 100.0
    assert candles[-1]["close"] == 106.0
