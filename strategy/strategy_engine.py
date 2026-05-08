from strategy.patterns import (
    bullish_engulfing,
    bearish_engulfing
)


class StrategyEngine:

    def __init__(self, candle_reader):

        self.reader = candle_reader

    # =====================================
    # SIDEWAYS FILTER
    # =====================================
    def is_sideways(self, symbol):

        candles = self.reader.get_last(
            symbol,
            5
        )

        # need enough candles
        if len(candles) < 5:
            return True

        highest = max(
            c["high"]
            for c in candles
        )

        lowest = min(
            c["low"]
            for c in candles
        )

        range_size = (
            highest - lowest
        )

        print(
            f"5 Candle Range = "
            f"{range_size}"
        )

        # sideways threshold
        return range_size < 5

    # =====================================
    # MAIN SIGNAL LOGIC
    # =====================================
    def generate_signal(self, symbol):

        # -------------------------
        # SIDEWAYS CHECK
        # -------------------------
        if self.is_sideways(symbol):

            print(
                "⛔ Sideways Market"
            )

            return None

        candles = self.reader.get_last(
            symbol,
            2
        )

        if len(candles) < 2:
            return None

        prev = candles[0]

        curr = candles[1]

        # -------------------------
        # BUY CALL
        # -------------------------
        if bullish_engulfing(
            prev,
            curr
        ):

            print(
                "🟢 Bullish Engulfing"
            )

            return "BUY_CE"

        # -------------------------
        # BUY PUT
        # -------------------------
        if bearish_engulfing(
            prev,
            curr
        ):

            print(
                "🔴 Bearish Engulfing"
            )

            return "BUY_PE"

        return None