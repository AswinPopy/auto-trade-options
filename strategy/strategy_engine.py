from strategy.indicators import (
    calculate_ema,
    calculate_vwap
)


class StrategyEngine:

    def __init__(self, candle_reader):

        self.reader = candle_reader

    # =====================================
    # EMA TREND
    # =====================================
    def ema_trend(self, closes):

        ema = calculate_ema(
            closes,
            20
        )

        if len(ema) < 2:
            return None

        # rising EMA
        if ema[-1] > ema[-2]:

            print("📈 EMA RISING")

            return "UP"

        # falling EMA
        if ema[-1] < ema[-2]:

            print("📉 EMA FALLING")

            return "DOWN"

        return None

    # =====================================
    # STRONG CANDLE
    # =====================================
    def strong_candle(
        self,
        candle
    ):

        body = abs(
            candle["close"]
            - candle["open"]
        )

        print(
            f"Body Size = {body}"
        )

        return body >= 0.75

    # =====================================
    # VOLUME SPIKE
    # =====================================
    def volume_spike(
        self,
        candles
    ):

        current_volume = candles[-1]["volume"]

        avg_volume = (
            sum(
                c["volume"]
                for c in candles[:-1]
            )
            / (len(candles) - 1)
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
            > avg_volume * 2
        )

    # =====================================
    # SMALL PULLBACK
    # =====================================
    def small_pullback(
        self,
        candles,
        trend
    ):

        if len(candles) < 3:
            return False

        c1 = candles[-3]
        c2 = candles[-2]
        c3 = candles[-1]

        # CE pullback
        if trend == "UP":

            return (
                c2["close"]
                < c1["close"]
                and
                c3["close"]
                > c2["close"]
            )

        # PE pullback
        if trend == "DOWN":

            return (
                c2["close"]
                > c1["close"]
                and
                c3["close"]
                < c2["close"]
            )

        return False

    # =====================================
    # WEAK PULLBACK VOLUME
    # =====================================
    def weak_pullback_volume(
        self,
        candles
    ):

        if len(candles) < 3:
            return False

        trend_volume = candles[-3]["volume"]

        pullback_volume = candles[-2]["volume"]

        return (
            pullback_volume
            < trend_volume
        )

    # =====================================
    # VWAP RESPECTED
    # =====================================
    def vwap_respected(
        self,
        candle,
        vwap,
        trend
    ):

        if trend == "UP":

            return (
                candle["low"]
                >= vwap
            )

        if trend == "DOWN":

            return (
                candle["high"]
                <= vwap
            )

        return False

    # =====================================
    # BREAKOUT
    # =====================================
    def breakout(
        self,
        candles,
        trend
    ):

        if len(candles) < 3:
            return False

        pullback = candles[-2]

        current = candles[-1]

        # CE breakout
        if trend == "UP":

            return (
                current["high"]
                > pullback["high"]
            )

        # PE breakout
        if trend == "DOWN":

            return (
                current["low"]
                < pullback["low"]
            )

        return False

    # =====================================
    # MAIN STRATEGY
    # =====================================
    def generate_signal(
        self,
        symbol
    ):

        candles = self.reader.get_last(
            symbol,
            25
        )

        if len(candles) < 25:
            return None

        closes = [
            c["close"]
            for c in candles
        ]

        current_price = closes[-1]

        # -------------------------
        # VWAP
        # -------------------------
        vwap = calculate_vwap(
            candles
        )

        print(f"VWAP = {vwap}")

        # -------------------------
        # EMA TREND
        # -------------------------
        trend = self.ema_trend(
            closes
        )

        if trend is None:
            return None

        # =========================
        # BUY CE CONDITIONS
        # =========================
        if trend == "UP":

            if current_price <= vwap:

                print(
                    "⛔ Price Below VWAP"
                )

                return None

            if not self.small_pullback(
                candles,
                trend
            ):

                print(
                    "⛔ No Pullback"
                )

                return None

            if not self.weak_pullback_volume(
                candles
            ):

                print(
                    "⛔ Pullback Volume Strong"
                )

                return None

            if not self.vwap_respected(
                candles[-1],
                vwap,
                trend
            ):

                print(
                    "⛔ VWAP Not Respected"
                )

                return None

            if not self.strong_candle(
                candles[-1]
            ):

                print(
                    "⛔ Weak Green Candle"
                )

                return None

            if not self.volume_spike(
                candles[-5:]
            ):

                print(
                    "⛔ No Volume Spike"
                )

                return None

            if not self.breakout(
                candles,
                trend
            ):

                print(
                    "⛔ No Breakout"
                )

                return None

            print(
                "🟢 BUY CE SIGNAL"
            )

            return "BUY_CE"

        # =========================
        # BUY PE CONDITIONS
        # =========================
        if trend == "DOWN":

            if current_price >= vwap:

                print(
                    "⛔ Price Above VWAP"
                )

                return None

            if not self.small_pullback(
                candles,
                trend
            ):

                print(
                    "⛔ No Pullback"
                )

                return None

            if not self.weak_pullback_volume(
                candles
            ):

                print(
                    "⛔ Pullback Volume Strong"
                )

                return None

            if not self.vwap_respected(
                candles[-1],
                vwap,
                trend
            ):

                print(
                    "⛔ VWAP Not Respected"
                )

                return None

            if not self.strong_candle(
                candles[-1]
            ):

                print(
                    "⛔ Weak Red Candle"
                )

                return None

            if not self.volume_spike(
                candles[-5:]
            ):

                print(
                    "⛔ No Volume Spike"
                )

                return None

            if not self.breakout(
                candles,
                trend
            ):

                print(
                    "⛔ No Breakdown"
                )

                return None

            print(
                "🔴 BUY PE SIGNAL"
            )

            return "BUY_PE"

        return None