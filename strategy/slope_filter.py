def calculate_daily_slope(candles):
    """Calculate the slope of a simple line from the first candle's open to the last candle's close."""
    if not candles:
        return 0.0

    if len(candles) < 2:
        return 0.0

    first_open = candles[0].get("open", 0)
    last_close = candles[-1].get("close", candles[-1].get("open", 0))
    x_distance = len(candles) - 1

    if x_distance == 0:
        return 0.0

    return (last_close - first_open) / x_distance


def should_allow_trade(signal, candles):
    """Allow buy signals only when the daily slope matches the signal direction."""
    if signal == "BUY_CE":
        return calculate_daily_slope(candles) > 0

    if signal == "BUY_PE":
        return calculate_daily_slope(candles) < 0

    return True
