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

        print(
            f"{position} PnL = {pnl}"
        )

        # ==========================
        # RISK SETTINGS
        # ==========================
        target = (
            self.broker.capital
            * 0.022
        )

        stoploss = (
            self.broker.capital
            * 0.0125
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
        if "26MAY" not in position:
            return False

        underlying = (
            position.split("26MAY")[0]
        )

        # ==========================
        # GET CANDLES
        # ==========================
        candles = (
            self.candle_engine
            .get_last(
                underlying,
                25
            )
        )

        if len(candles) < 25:
            return False

        closes = [
            c["close"]
            for c in candles
        ]

        current_stock_price = (
            closes[-1]
        )

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


    # =====================================
    # CLEAR POSITION MEMORY
    # =====================================
    def clear_position(
        self,
        position
    ):

        if position in self.max_pnl:

            del self.max_pnl[position]