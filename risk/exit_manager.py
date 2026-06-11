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
        position,
        current_price
        ):

        entry = self.broker.positions[
            position
        ]

        qty = self.broker.quantity[
            position
        ]

        pnl = (
            (current_price - entry)
            * qty
        )
        print(f"Current price cal pnl = {current_price} -- {entry} -- {qty}")
        print(
            f"{position} PnL = {pnl}"
        )

        # ==========================
        # RISK SETTINGS
        # ==========================
        target = (
            self.broker.capital
            * 0.050
        )

        stoploss = (
            self.broker.capital
            * 0.025
        )

        # ==========================
        # HARD STOPLOSS
        # ==========================
        if pnl <= -stoploss:

            print(
                "🔴 HARD STOPLOSS HIT"
            )

            return True

        # ==========================
        # TRACK MAX PNL
        # ==========================
        if (
            position
            not in self.max_pnl
        ):

            self.max_pnl[position] = pnl

        self.max_pnl[position] = max(
            self.max_pnl[position],
            pnl
        )

        max_seen = self.max_pnl[
            position
        ]

      
        if max_seen >= target:

            trailing_buffer = (
                target * 0.15
            )

            trailing_level = (
                max_seen
                - trailing_buffer
            )

            print(
                f"Trailing Level = "
                f"{trailing_level}"
            )

            if pnl <= trailing_level:

                print(
                    "🟠 TRAILING STOP HIT"
                )

                return True

        # ==========================
        # GET UNDERLYING
        # ==========================
        if "26JUN" not in position:
            return False

        underlying = (
            position.split("26JUN")[0]
        )

        # ==========================
        # GET CANDLES
        # ==========================
        candles = (
            self.candle_engine
            .get_last(
                underlying,
                60
            )
        )

        if len(candles) < 60:
            return False

        closes = [
            c["close"]
            for c in candles
        ]

        current_stock_price = (
            closes[-1]
        )

        atr = self.calculate_atr(candles)
        if atr is None:
            return False

        # ==========================
        # EMA
        # ==========================
        ema = calculate_ema(
            closes,
            20
        )

        if len(ema) < 20:
            return False

        current_ema = ema[-1]

        # ==========================
        # VWAP
        # ==========================
        vwap = calculate_vwap(
            candles
        )


        vwap_buffer = (
            current_stock_price
            * 0.0015
        )

        # =================================
        # CE EXIT CONDITIONS
        # =================================
        if "CE" in position:

            # ATR-based stop loss / target for CE
            ce_stop_loss = (
                current_price
                - (1.5 * atr)
            )
            ce_target = (
                current_price
                + (2.0 * atr)
            )

            if current_price <= ce_stop_loss:

                print(
                    "🔴 CE ATR STOP LOSS HIT",
                    f"level={ce_stop_loss:.2f}"
                )

                return True

            if current_price >= ce_target:

                print(
                    "🟢 CE ATR TARGET HIT",
                    f"level={ce_target:.2f}"
                )

                return True

            # strong VWAP loss
            if (
                current_stock_price
                < (vwap - vwap_buffer)
            ):

                print(
                    "🔴 CE EXIT BELOW VWAP"
                )

                return True

            # price below EMA
            if (
                current_stock_price
                < current_ema
            ):

                print(
                    "🔴 CE EXIT BELOW EMA"
                )

                return True

        # =================================
        # PE EXIT CONDITIONS
        # =================================
        if "PE" in position:

            # ATR-based stop loss / target for PE
            pe_stop_loss = (
                current_price
                + (1.5 * atr)
            )
            pe_target = (
                current_price
                - (2.0 * atr)
            )

            if current_price >= pe_stop_loss:

                print(
                    "🔴 PE ATR STOP LOSS HIT",
                    f"level={pe_stop_loss:.2f}"
                )

                return True

            if current_price <= pe_target:

                print(
                    "🟢 PE ATR TARGET HIT",
                    f"level={pe_target:.2f}"
                )

                return True

            # strong VWAP reclaim
            if (
                current_stock_price
                > (vwap + vwap_buffer)
            ):

                print(
                    "🔴 PE EXIT ABOVE VWAP"
                )

                return True

            # price above EMA
            if (
                current_stock_price
                > current_ema
            ):

                print(
                    "🔴 PE EXIT ABOVE EMA"
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