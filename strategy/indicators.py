def calculate_ema(prices, period=20):

    if len(prices) < period:
        return []

    ema_values = []

    multiplier = (
        2 / (period + 1)
    )

    sma = sum(
        prices[:period]
    ) / period

    ema_values.append(sma)

    for price in prices[period:]:

        ema = (
            (price - ema_values[-1])
            * multiplier
        ) + ema_values[-1]

        ema_values.append(ema)

    return ema_values


def calculate_vwap(candles):

    total_price_volume = 0

    total_volume = 0

    for c in candles:

        typical_price = (
            c["high"]
            + c["low"]
            + c["close"]
        ) / 3

        total_price_volume += (
            typical_price
            * c["volume"]
        )

        total_volume += c["volume"]

    if total_volume == 0:
        return 0

    return (
        total_price_volume
        / total_volume
    )