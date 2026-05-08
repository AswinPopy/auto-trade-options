from collections import defaultdict
from datetime import datetime


class CandleEngine:

    def __init__(self):
        self.current = {}
        self.history = defaultdict(list)

    def update_tick(self, symbol, price):

        now = datetime.now()
        minute = now.hour * 60 + now.minute

        if symbol not in self.current:

            self.current[symbol] = {
                "minute": minute,
                "open": price,
                "high": price,
                "low": price,
                "close": price
            }

            return None

        c = self.current[symbol]

        # same candle
        if c["minute"] == minute:

            c["high"] = max(c["high"], price)
            c["low"] = min(c["low"], price)
            c["close"] = price

            return None

        # candle completed
        completed = c.copy()
        self.history[symbol].append(completed)

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