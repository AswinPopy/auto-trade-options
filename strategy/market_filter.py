def is_sideways(candles, threshold=0.15):

    """
    Detect sideways market.

    threshold = percentage move
    """

    if len(candles) < 5:
        return False

    ranges = []

    for candle in candles:

        high = candle["high"]
        low = candle["low"]
        close = candle["close"]

        move_percent = (
            (high - low) / close
        ) * 100

        ranges.append(move_percent)

    avg_range = sum(ranges) / len(ranges)

    return avg_range < threshold