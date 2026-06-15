from strategy.indicators import (
    calculate_ema,
    calculate_vwap
)


class ExitManager:

    def __init__(
        self,
        candle_engine,
        broker
    ):

        self.candle_engine = (
            candle_engine
        )

        self.broker = broker

        # stores highest pnl seen
        self.max_pnl = {}

    # =====================================
    # MAIN EXIT CHECK
    # =====================================
    def should_exit(
    self,
    position
    ):
        """
        Exit based purely on underlying ATR movement.
        """

        details = self.broker.trade_details.get(
            position,
            {}
        )

        underlying = details.get(
            "underlying"
        )

        entry_underlying = details.get(
            "underlying_entry"
        )

        if (
            underlying is None
            or entry_underlying is None
        ):
            return False

        candles = self.candle_engine.get_last(
            underlying,
            25
        )

        if len(candles) < 25:
            return False

        closes = [
            c["close"]
            for c in candles
        ]

        current_underlying = closes[-1]

        atr = self.calculate_atr(
            candles[-20:]
        )

        if atr is None:
            return False

        # ==================================
        # CALL OPTION
        # ==================================
        print("ATR Exit Check: {atr} | Current Underlying={current} | Entry Underlying={entry}")
        if "CE" in position:

            stop_level = (
                entry_underlying
                - (1.5 * atr)
            )

            target_level = (
                entry_underlying
                + (2.0 * atr)
            )

            print(
                f"CE | Entry={entry_underlying}"
                f" Current={current_underlying}"
                f" ATR={atr}"
                f" SL={stop_level}"
                f" TG={target_level}"
            )

            if current_underlying <= stop_level:

                print(
                    "🔴 CE ATR STOPLOSS HIT"
                )

                return True

            if current_underlying >= target_level:

                print(
                    "🟢 CE ATR TARGET HIT"
                )

                return True

        # ==================================
        # PUT OPTION
        # ==================================

        elif "PE" in position:

            stop_level = (
                entry_underlying
                + (1.5 * atr)
            )

            target_level = (
                entry_underlying
                - (2.0 * atr)
            )

            print(
                f"PE | Entry={entry_underlying}"
                f" Current={current_underlying}"
                f" ATR={atr}"
                f" SL={stop_level}"
                f" TG={target_level}"
            )

            if current_underlying >= stop_level:

                print(
                    "🔴 PE ATR STOPLOSS HIT"
                )

                return True

            if current_underlying <= target_level:

                print(
                    "🟢 PE ATR TARGET HIT"
                )

                return True

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

        # Seed with SMA of first 14 TRs
        atr = sum(trs[:period]) / period

        # Wilder's smoothing for remaining TRs
        for tr in trs[period:]:
            atr = (
                (atr * (period - 1) + tr)
                / period
            )

        return atr


    # =====================================
    # CLEAR POSITION MEMORY
    # =====================================
    def clear_position(
        self,
        position
    ):

        if position in self.max_pnl:

            del self.max_pnl[position]