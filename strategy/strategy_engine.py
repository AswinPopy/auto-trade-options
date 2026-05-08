from strategy.patterns import (
    bullish_engulfing,
    bearish_engulfing
)

from datetime import datetime


class StrategyEngine:

    def __init__(self, candle_reader):

        self.reader = candle_reader

    # =====================================
    # TIME FILTER
    # =====================================
    def valid_time(self):

        now = datetime.now()

        total_minutes = (
            now.hour * 60
            + now.minute
        )

        market_open = (
            9 * 60 + 20
        )

        market_close = (
            15 * 60 + 15
        )

        lunch_start = (
            12 * 60
        )

        lunch_end = (
            13 * 60 + 30
        )

        # before market time
        if total_minutes < market_open:

            print(
                "⛔ Before Trading Window"
            )

            return False

        # lunch sideways
        if (
            lunch_start
            <= total_minutes
            <= lunch_end
        ):

            print(
                "⛔ Lunch Sideways Time"
            )

            return False

        # after allowed time
        if total_minutes > market_close:

            print(
                "⛔ Market Closing Time"
            )

            return False

        return True

    # =====================================
    # SIDEWAYS FILTER
    # =====================================
    def is_sideways(self, symbol):

        candles = self.reader.get_last(
            symbol,
            5
        )

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
            f"{range_size:.2f}"
        )

        return range_size < 5

    # =====================================
    # TREND FILTER
    # =====================================
    def get_trend(self, symbol):

        candles = self.reader.get_last(
            symbol,
            5
        )

        if len(candles) < 5:
            return None

        first_close = candles[0]["close"]

        last_close = candles[-1]["close"]

        if last_close > first_close:

            print("📈 UPTREND")

            return "UP"

        elif last_close < first_close:

            print("📉 DOWNTREND")

            return "DOWN"

        return None

    # =====================================
    # STRONG CANDLE
    # =====================================
    def strong_candle(self, candle):

        body_size = abs(
            candle["close"]
            - candle["open"]
        )

        print(
            f"Candle Body = "
            f"{body_size:.2f}"
        )

        return body_size >= 2

    # =====================================
    # VOLUME CONFIRMATION
    # =====================================
    def volume_confirmed(
        self,
        symbol
    ):

        candles = self.reader.get_last(
            symbol,
            5
        )

        if len(candles) < 5:
            return False

        current_volume = candles[-1]["volume"]

        avg_volume = (
            sum(
                c["volume"]
                for c in candles[:-1]
            )
            / 4
        )

        print(
            f"Current Volume = "
            f"{current_volume}"
        )

        print(
            f"Average Volume = "
            f"{avg_volume}"
        )

        return (
            current_volume
            > avg_volume
        )

    # =====================================
    # BREAKOUT
    # =====================================
    def breakout_confirmed(
        self,
        prev,
        curr,
        signal
    ):

        if signal == "BUY_CE":

            return (
                curr["high"]
                > prev["high"]
            )

        if signal == "BUY_PE":

            return (
                curr["low"]
                < prev["low"]
            )

        return False

    # =====================================
    # MAIN SIGNAL ENGINE
    # =====================================
    def generate_signal(self, symbol):

        # -------------------------
        # TIME FILTER
        # -------------------------
        if not self.valid_time():

            return None

        # -------------------------
        # SIDEWAYS FILTER
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
        # TREND FILTER
        # -------------------------
        trend = self.get_trend(symbol)

        if trend is None:
            return None

        # -------------------------
        # STRONG CANDLE
        # -------------------------
        if not self.strong_candle(curr):

            print(
                "⛔ Weak Candle"
            )

            return None

        # -------------------------
        # VOLUME CONFIRMATION
        # -------------------------
        if not self.volume_confirmed(
            symbol
        ):

            print(
                "⛔ Weak Volume"
            )

            return None

        # =========================
        # BUY CE
        # =========================
        if (
            bullish_engulfing(
                prev,
                curr
            )
            and trend == "UP"
        ):

            signal = "BUY_CE"

            if self.breakout_confirmed(
                prev,
                curr,
                signal
            ):

                print(
                    "🟢 BUY CE CONFIRMED"
                )

                return signal

            print(
                "⛔ No Bullish Breakout"
            )

        # =========================
        # BUY PE
        # =========================
        if (
            bearish_engulfing(
                prev,
                curr
            )
            and trend == "DOWN"
        ):

            signal = "BUY_PE"

            if self.breakout_confirmed(
                prev,
                curr,
                signal
            ):

                print(
                    "🔴 BUY PE CONFIRMED"
                )

                return signal

            print(
                "⛔ No Bearish Breakout"
            )

        return None