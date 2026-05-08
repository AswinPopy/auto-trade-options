from strategy.patterns import (
    bullish_engulfing,
    bearish_engulfing
)

from strategy.market_filter import (
    is_sideways
)


class StrategyEngine:

    def __init__(self, candle_reader):

        self.reader = candle_reader

    def generate_signal(self, symbol):

        candles = self.reader.get_recent_candles(
            symbol,
            5
        )

        if len(candles) < 5:
            return "HOLD"

        # --------------------------------
        # SIDEWAYS FILTER
        # --------------------------------
        if is_sideways(candles):

            print("⚠️ SIDEWAYS MARKET")

            return "HOLD"

        prev = candles[-2]
        curr = candles[-1]

        # --------------------------------
        # PATTERNS
        # --------------------------------
        if bullish_engulfing(prev, curr):
            return "BUY"

        if bearish_engulfing(prev, curr):
            return "SELL"

        return "HOLD"