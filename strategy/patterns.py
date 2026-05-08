def bullish_engulfing(prev, curr):

    return (
        prev["close"] < prev["open"] and
        curr["close"] > curr["open"] and
        curr["close"] > prev["open"]
    )


def bearish_engulfing(prev, curr):

    return (
        prev["close"] > prev["open"] and
        curr["close"] < curr["open"] and
        curr["close"] < prev["open"]
    )