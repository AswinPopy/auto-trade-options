from collections import defaultdict
from datetime import datetime


class CandleEngine:

    def __init__(self):

        self.current = {}

        self.history = defaultdict(list)

    def update_tick(
    self,
    symbol,
    price,
    volume
):

        now = datetime.now()
        today = now.date()

        minute = (
            now.hour * 60
            + now.minute
        )

        # first candle or new day
        if (
            symbol not in self.current
            or self.current[symbol].get("date") != today
        ):

            self.current[symbol] = {
                "date": today,
                "minute": minute,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume
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
            candle["volume"] += volume

            return None

        # candle complete
        completed = candle.copy()

        completed["date"] = today
        self.history[symbol].append(
            completed
        )

        # new candle
        self.current[symbol] = {
            "date": today,
            "minute": minute,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume
        }

        return completed

    def get_last(self, symbol, n=2):

        return self.history[symbol][-n:]

    def get_day_candles(self, symbol):

        today = datetime.now().date()
        candles = []

        for candle in self.history.get(symbol, []):
            if candle.get("date") in (None, today):
                candles.append(candle)

        if symbol in self.current:
            current_candle = self.current[symbol]
            if current_candle.get("date") in (None, today):
                candles.append(current_candle.copy())

        return candles