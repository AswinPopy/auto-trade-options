from utils.trade_logger import (
    TradeLogger
)
import time
from broker.kite_session import kite
from datetime import datetime
class PaperBroker:

    def __init__(self):

        self.logger = TradeLogger()

        self.capital = self.logger.get_last_capital()

        self.positions = {}

        self.quantity = {}

        self.realized_pnl = 0

        self.live_trading = False

        self.order_ids = {}

    # =========================
    # BUY
    # =========================
    def buy(
        self,
        symbol,
        avg_price,
        qty
        ):
        print(f"INSIDE BUY : {symbol}")
        now = datetime.now()

        current_min = (
            now.hour * 60
            + now.minute
        )

        # Do not buy after 1:30 PM
        if current_min > (13 * 60 + 30):

            return

        # already exists
        if symbol in self.positions:
            print(f"SYMBOL NOT IN POSITIONS BUY : {symbol}")
            return

        if self.live_trading:

            order_id = kite.place_order(

                variety=kite.VARIETY_REGULAR,

                exchange=kite.EXCHANGE_NFO,

                tradingsymbol=symbol,

                transaction_type=
                kite.TRANSACTION_TYPE_BUY,

                quantity=qty,

                product=kite.PRODUCT_MIS,

                order_type=
                kite.ORDER_TYPE_MARKET
            )

            print(
                f"LIVE BUY ORDER : "
                f"{order_id}"
            )

            actual_avg_price = None

            for _ in range(10):

                order_history = (
                    kite.order_history(
                        order_id
                    )
                )

                latest = max(
                    order_history,
                    key=lambda x: x["order_timestamp"]
                    )


                status = latest["status"]

                if status == "COMPLETE":
                    
                    self.order_ids[symbol] = order_id
                    actual_avg_price = (
                        float(latest["average_price"])
                    )

                    break

                if status in [
                    "REJECTED",
                    "CANCELLED"
                    ]:

                    print(
                        f"❌ ORDER {status}"
                    )

                    return
                time.sleep(0.5)

            if actual_avg_price is None:

                print(
                    "❌ ORDER NOT FILLED"
                )

                return

            self.positions[symbol] = (
                actual_avg_price
            )
            filled_qty = latest["filled_quantity"]

            self.quantity[symbol] = (
            filled_qty
            )

        else:
            self.positions[symbol] = (
                avg_price
            )

            self.quantity[symbol] = qty

        print(
            f"🟢 BOUGHT "
            f"{symbol} "
            f"Qty={self.quantity[symbol]} "
            f"AvgPrice={self.positions[symbol]}"
            )

    # =========================
    # SELL
    # =========================
    def sell(
        self,
        symbol,
        price
        ):

        order_id = None

        if symbol not in self.positions:

            return

        entry = self.positions[symbol]

        qty = self.quantity[symbol]

        # ==========================
        # LIVE EXIT
        # ==========================
        if self.live_trading:

            order_id = kite.place_order(

                variety=kite.VARIETY_REGULAR,

                exchange=kite.EXCHANGE_NFO,

                tradingsymbol=symbol,

                transaction_type=
                kite.TRANSACTION_TYPE_SELL,

                quantity=qty,

                product=kite.PRODUCT_MIS,

                order_type=
                kite.ORDER_TYPE_MARKET
            )

            print(
                f"LIVE SELL ORDER : "
                f"{order_id}"
            )

            actual_exit_price = None

            for _ in range(10):

                order_history = (
                    kite.order_history(
                        order_id
                    )
                )

                latest = max(
                    order_history,
                    key=lambda x: x["order_timestamp"]
                )

                status = latest["status"]

                if status == "COMPLETE":

                    actual_exit_price = (
                        float(
                            latest[
                                "average_price"
                            ]
                        )
                    )

                    qty = latest[
                        "filled_quantity"
                    ]

                    break

                if status in [
                    "REJECTED",
                    "CANCELLED"
                ]:

                    print(
                        f"❌ SELL ORDER "
                        f"{status}"
                    )

                    return

                time.sleep(0.5)

            if actual_exit_price is None:

                print(
                    "❌ SELL NOT FILLED"
                )

                return

            price = actual_exit_price

        # ==========================
        # PnL
        # ==========================
        pnl = (
            (price - entry)
            * qty
        )

        self.realized_pnl += pnl

        self.capital += pnl
        
        self.logger.log_trade(
            order_id,
            symbol,
            entry,
            price,
            qty,
            pnl
        )

        print(
            f"🔴 SOLD "
            f"{symbol} "
            f"@ {price}"
        )

        print(
            f"PnL = {pnl:.2f}"
        )

        del self.positions[symbol]

        del self.quantity[symbol]

    
