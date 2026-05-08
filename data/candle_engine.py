from collections import defaultdict
from datetime import datetime


class CandleEngine:

    def __init__(self):

        self.current = {}

        self.history = defaultdict(list)

    def update_tick(self, symbol, price):

        now = datetime.now()

        minute = (
            now.hour * 60
            + now.minute
        )

        # first candle
        if symbol not in self.current:

            self.current[symbol] = {
                "minute": minute,
                "open": price,
                "high": price,
                "low": price,
                "close": price
            }

            return None

        candle = self.current[symbol]

        # same candle
        if candle["minute"] == minute:

            candle["high"] = max(
                candle["high"],
                price
            )

            candle["low"] = min(
                candle["low"],
                price
            )

            candle["close"] = price

            return None

        # candle complete
        completed = candle.copy()

        self.history[symbol].append(
            completed
        )

        # new candle
        self.current[symbol] = {
            "minute": minute,
            "open": price,
            "high": price,
            "low": price,
            "close": price
        }

        return completed

    def get_last(self, symbol, n=2):

        return self.history[symbol][-n:]