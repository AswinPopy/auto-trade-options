import logging

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
    def ema_trend(
    self,
    closes
):

        ema = calculate_ema(
            closes,
            20
        )

        if len(ema) < 5:
            return None

        slope_percent = (
            (
                ema[-1]
                - ema[-5]
            )
            /
            ema[-5]
        ) * 100

        current_price = closes[-1]

        current_ema = ema[-1]

        # bullish
        if (
            slope_percent > 0.1
            and current_price > current_ema
        ):

            return "UP"

        # bearish
        if (
            slope_percent < -0.1
            and current_price < current_ema
        ):

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

        total_range = (
            candle["high"]
            - candle["low"]
        )

        if total_range == 0:
            return False

        body_strength = (
            body
            / total_range
        )

        print(
            f"Body Strength = "
            f"{body_strength}"
        )

        return (
            body_strength >= 0.63
        )

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

        tolerance = (
            vwap * 0.001
        )

        if trend == "UP":

            return (
                candle["low"]
                >= vwap - tolerance
            )

        if trend == "DOWN":

            return (
                candle["high"]
                <= vwap + tolerance
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
                current["close"]
                > pullback["high"]
            )

        # PE breakout
        if trend == "DOWN":

            return (
                current["close"]
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

        print(f"VWAP {symbol} = {vwap}")

        # -------------------------
        # EMA TREND
        # -------------------------
        trend = self.ema_trend(
            closes
        )
        print(f"CURRENT TREND {symbol} : {trend}")
        if trend is None:
            logging.info("RETURN : No trend")
            return None

        # =========================
        # BUY CE CONDITIONS
        # =========================
        if trend == "UP":

            if current_price <= vwap:
                logging.info(f"Current price {symbol} : {current_price}")
                logging.info(f"vwap : {vwap}")
                print(
                    "⛔ Price Below VWAP"
                )
                return None

            print(
                    "🟢 Price above VWAP : CE"
                )
            
            if not self.small_pullback(
                candles,
                trend
            ):
                print(
                    "⛔ No Pullback"
                )

                return None

            print(
                    "🟢 Strong Pullback : CE"
                )
            
            if not self.weak_pullback_volume(
                candles
            ):

                print(
                    "⛔ Pullback Volume Strong"
                )

                return None

            print(
                    "🟢 Pullback Volume Not Strong : CE"
                )
            
            if not self.vwap_respected(
                candles[-2],
                vwap,
                trend
            ):
                print(
                    "⛔ VWAP Not Respected"
                )

                return None

            print(
                    "🟢 VWAP Respected : CE"
                )
            
            if not self.strong_candle(
                candles[-1]
            ):
                print(
                    "⛔ Weak Green Candle"
                )

                return None

            print(
                    "🟢 Strong Green Candle : CE"
                )
            
            if not self.volume_spike(
                candles[-5:]
            ):

                print(
                    "⛔ No Volume Spike"
                )

                return None

            print(
                    "🟢 Volume spike : CE"
                )
            
            if not self.breakout(
                candles,
                trend
            ):
                print(
                    "⛔ No Breakout"
                )

                return None
            
            print(
                    "🟢 Volume Breakout : CE"
                )
            
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

            print(
                    "🟡 Price BELOW VWAP : PE"
                )
            
            if not self.small_pullback(
                candles,
                trend
            ):
                print(
                    "⛔ No Pullback"
                )

                return None
            
            print(
                    "🟡 Strong Pullback : PE"
                )

            if not self.weak_pullback_volume(
                candles
            ):
                print(
                    "⛔ Pullback Volume Strong"
                )

                return None

            if not self.vwap_respected(
                candles[-2],
                vwap,
                trend
            ):
                print(
                    "⛔ VWAP Not Respected"
                )

                return None

            print(
                    "🟡 VWAP Respected : PE"
                )
            
            if not self.strong_candle(
                candles[-1]
            ):
                print(
                    "⛔ Weak Red Candle"
                )

                return None

            print(
                    "🟡 Strong RED Candle : PE"
                )
            
            if not self.volume_spike(
                candles[-5:]
            ):
                print(
                    "⛔ No Volume Spike"
                )

                return None

            print(
                    "🟡 Volume spike : PE"
                )
            
            if not self.breakout(
                candles,
                trend
            ):
                print(
                    "⛔ No Breakdown"
                )

                return None
            
            print(
                    "🟡 Volume Breakout : PE"
                )
            
            print(
                "🟡 BUY PE SIGNAL"
            )

            return "BUY_PE"

        return None