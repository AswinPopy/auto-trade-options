def bullish_engulfing(prev, curr):

    prev_red = (
        prev["close"]
        < prev["open"]
    )

    curr_green = (
        curr["close"]
        > curr["open"]
    )

    engulf = (
        curr["open"]
        < prev["close"]
        and
        curr["close"]
        > prev["open"]
    )

    return (
        prev_red
        and curr_green
        and engulf
    )


def bearish_engulfing(prev, curr):

    prev_green = (
        prev["close"]
        > prev["open"]
    )

    curr_red = (
        curr["close"]
        < curr["open"]
    )

    engulf = (
        curr["open"]
        > prev["close"]
        and
        curr["close"]
        < prev["open"]
    )

    return (
        prev_green
        and curr_red
        and engulf
    )