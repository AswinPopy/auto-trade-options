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
        current_price,
        live_prices
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
        # HARD STOPLOSS
        # ==========================
        if pnl <= -500:

            print(
                "🔴 HARD STOPLOSS HIT"
            )

            return True

        # ==========================
        # TRACK MAX PnL
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

        # ==========================
        # TRAILING STOP
        # ==========================
        if max_seen >= 1000:

            trailing_level = (
                max_seen - 500
            )

            if pnl <= trailing_level:
                print(
                    "🟠 TRAILING STOP HIT"
                )
                
                return True

        # ==========================
        # GET UNDERLYING STOCK
        # ==========================
        if "CE" in position:

            underlying = (
                position.split("CE")[0]
            )

        elif "PE" in position:

            underlying = (
                position.split("PE")[0]
            )

        else:
            return False

        # remove expiry/strike noise
        if "HDFCBANK" in underlying:
            underlying = "HDFCBANK"

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

        # ==========================
        # EMA
        # ==========================
        ema = calculate_ema(
            closes,
            20
        )

        if len(ema) < 2:
            return False

        ema_up = (
            ema[-1]
            > ema[-2]
        )

        ema_down = (
            ema[-1]
            < ema[-2]
        )

        # ==========================
        # VWAP
        # ==========================
        vwap = calculate_vwap(
            candles
        )

        current_stock_price = (
            closes[-1]
        )

        # =================================
        # CE EXIT CONDITIONS
        # =================================
        if "CE" in position:

            # price below VWAP
            if (
                current_stock_price
                < vwap
            ):

                print(
                    "🔴 CE EXIT BELOW VWAP"
                )

                return True

            # EMA reversal
            if ema_down:

                print(
                    "🔴 CE EXIT EMA DOWN"
                )

                return True

        # =================================
        # PE EXIT CONDITIONS
        # =================================
        if "PE" in position:

            # price above VWAP
            if (
                current_stock_price
                > vwap
            ):

                print(
                    "🔴 PE EXIT ABOVE VWAP"
                )

                return True

            # EMA reversal
            if ema_up:

                print(
                    "🔴 PE EXIT EMA UP"
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