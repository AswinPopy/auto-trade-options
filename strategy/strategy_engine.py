from datetime import datetime

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

        current_price = closes[-1] # 138.30
 
        current_ema = ema[-1] # 139.45935774849838
        # ema[-3] 139.68364755425978
        # bullish
        if (
            ema[-1] > ema[-3]
            and current_price > current_ema
        ):

            return "UP"

        # bearish
        if (
            ema[-1] < ema[-3]
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
            return False, 0

        body_strength = (
            body
            / total_range
        )
        print(datetime.now())
        print(
            f"Body Strength = "
            f"{body_strength}"
        )

        return (
            body_strength >= 0.65, body_strength
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
                c2["close"] < c2["open"]
                and
                abs(c2["close"] - c2["open"])
                <
                abs(c1["close"] - c1["open"])
                and
                c3["close"] > c3["open"]
            )

        if trend == "DOWN":

            return (
                c2["close"] > c2["open"]
                and
                abs(c2["close"] - c2["open"])
                <
                abs(c1["close"] - c1["open"])
                and
                c3["close"] < c3["open"]
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

    def calculate_atr(
        self,
        candles,
        period=14
    ):

        if len(candles) < period + 1:
            return None

        trs = []

        for i in range(1, len(candles)):

            high = candles[i]["high"]

            low = candles[i]["low"]

            prev_close = candles[i - 1]["close"]

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )

            trs.append(tr)

        atr = (
            sum(trs[-period:])
            / period
        )

        return atr
    
    def calculate_atr_series(
        self,
        candles,
        atr_period=14
    ):
        if len(candles) < atr_period + 20:
            return []

        trs = []

        for i in range(1, len(candles)):
            high = candles[i]["high"]
            low = candles[i]["low"]
            prev_close = candles[i - 1]["close"]

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )

            trs.append(tr)

        atr_values = []

        for i in range(atr_period - 1, len(trs)):
            atr = (
                sum(trs[i - atr_period + 1:i + 1])
                / atr_period
            )

            atr_values.append(atr)

        return atr_values
    
    # =====================================
    # MAIN STRATEGY
    # =====================================
    def generate_signal(
        self,
        symbol
    ):
        details = {}
        candles = self.reader.get_last(
            symbol,
            35
        )
        
        closes = [
            c["close"]
            for c in candles
        ]

        if len(candles) < 25:
            return None, None


        current_price = closes[-1]
        details['current_price'] = current_price
        # -------------------------
        # VWAP
        # -------------------------
        vwap = calculate_vwap(
            candles
        )
        print(datetime.now())
        print(f"VWAP {symbol} = {vwap}")
        details['vwap'] = vwap
        # -------------------------
        # EMA TREND
        # -------------------------
        trend = self.ema_trend(
            closes
        )
        print(f"CURRENT TREND {symbol} : {trend}")
        if trend is None:
            print("RETURN : No trend")
            return None, details

        atr_values = self.calculate_atr_series(
            candles,
            atr_period=14
        )

        if not atr_values:
            print(f"⛔ {symbol} : Not enough data for ATR")
            return None, details    
        
        current_atr = atr_values[-1]

        atr_20_period_average = (
            sum(atr_values[-20:])
            / 20
        )

        if atr_20_period_average == 0:
            return None, details

        atr_ratio = (
            current_atr
            / atr_20_period_average
        )
        if atr_ratio < 1.5:
            print(f"⛔ {symbol} : ATR Ratio {atr_ratio:.2f} below threshold")
            return None, details
        
        atr_percent = (
            current_atr / current_price
        ) * 100

        details['atr_percent'] = atr_percent

        if atr_percent < 0.11:
            print(f"⛔ {symbol} : ATR Percent {atr_percent:.2f}% below threshold")
            return None, details
        

        # =========================
        # BUY CE CONDITIONS
        # =========================
        if trend == "UP":

            if current_price <= vwap:
                print(f"Current price {symbol} : {current_price}")
                print(f"vwap : {vwap}")
                print(
                    f"⛔ {symbol} : Price Below VWAP"
                )
                return None, details

            print(
                    f"🟢 {symbol} : Price above VWAP : CE"
                )
            
            # if not self.small_pullback(
            #     candles,
            #     trend
            # ):
            #     print(
            #         f"⛔ {symbol} : No Pullback"
            #     )

            #     return None, details

            # print(
            #         f"🟢 {symbol} : Strong Pullback : CE"
            #     )
            
            # if not self.weak_pullback_volume(
            #     candles
            # ):

            #     print(
            #         f"⛔ {symbol} :  Pullback Volume Strong"
            #     )

            #     return None, details

            # print(
            #         f"🟢 {symbol} : Pullback Volume Not Strong : CE"
            #     )
            
            # if not self.vwap_respected(
            #     candles[-2],
            #     vwap,
            #     trend
            # ):
            #     print(
            #         f"⛔ {symbol} : VWAP Not Respected"
            #     )

            #     return None, details

            # print(
            #         f"🟢 {symbol} : VWAP Respected : CE"
            #     )
            
            candle_strong, candle_strength = self.strong_candle(candles[-1])
            if not candle_strong:
                print(
                    f"⛔ {symbol} : Weak Green Candle"
                )

                return None, details

            print(
                    f"🟢 {symbol} : Strong Green Candle : CE"
                )
            
            details['candle_strength'] = candle_strength
            # if not self.volume_spike(
            #     candles[-5:]
            # ):

            #     print(
            #         f"⛔ {symbol} : No Volume Spike"
            #     )

            #     return None, details

            # print(
            #         f"🟢 {symbol} : Volume spike : CE"
            #     )
            
            if not self.breakout(
                candles,
                trend
            ):
                print(
                    f"⛔ {symbol} No Breakout"
                )

                return None, details
            
            print(
                    f"🟢 {symbol} : Volume Breakout : CE"
                )
            
            print(
                f"🟢 {symbol} : BUY CE SIGNAL"
            )

            return "BUY_CE", details

        # =========================
        # BUY PE CONDITIONS
        # =========================
        if trend == "DOWN":

            if current_price >= vwap:
                print(
                    f"⛔ {symbol} : Price Above VWAP"
                )

                return None, details

            print(
                    f"🟡 {symbol} : Price BELOW VWAP : PE"
                )
            
            # if not self.small_pullback(
            #     candles,
            #     trend
            # ):
            #     print(
            #         f"⛔ {symbol} :  No Pullback"
            #     )

            #     return None, details
            
            # print(
            #         f"🟡 {symbol} : Strong Pullback : PE"
            #     )

            # if not self.weak_pullback_volume(
            #     candles
            # ):
            #     print(
            #         f"⛔ {symbol} : Pullback Volume Strong"
            #     )

            #     return None, details

            # if not self.vwap_respected(
            #     candles[-2],
            #     vwap,
            #     trend
            # ):
            #     print(
            #         f"⛔ {symbol} : VWAP Not Respected"
            #     )

            #     return None, details

            # print(
            #         f"🟡 {symbol} : VWAP Respected : PE"
            #     )
            
            candle_strong, candle_strength = self.strong_candle(candles[-1])
            if not candle_strong:
                print(
                    f"⛔ {symbol} : Weak Red Candle"
                )

                return None, details

            print(
                    f"🟡 {symbol} : Strong RED Candle : PE"
                )
            details['candle_strength'] = candle_strength

            # if not self.volume_spike(
            #     candles[-5:]
            # ):
            #     print(
            #         f"⛔ {symbol} : No Volume Spike"
            #     )

            #     return None, details

            # print(
            #         f"🟡 {symbol} : Volume spike : PE"
            #     )
            
            if not self.breakout(
                candles,
                trend
            ):
                print(
                    f"⛔ {symbol} : No Breakdown"
                )

                return None, details
            
            print(
                    f"🟡 {symbol} : Volume Breakout : PE"
                )
            
            print(
                f"🟡 {symbol} BUY PE SIGNAL"
            )

            return "BUY_PE", details

        return None, None