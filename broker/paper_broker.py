from utils.trade_logger import (
    TradeLogger
)
import time
from broker.kite_session import kite
from datetime import datetime
from config import LIVE_TRADING


class PaperBroker:

    def __init__(self):

        self.logger = TradeLogger()

        self.live_trading = LIVE_TRADING

        self.capital = (
            self._fetch_live_capital()
            if self.live_trading
            else self.logger.get_last_capital()
        )

        self.positions = {}

        self.quantity = {}

        self.realized_pnl = 0

        self.order_ids = {}
        self.trade_details = {}
        self.already_traded = set()

    def _fetch_live_capital(self):
        try:
            margins = kite.margins("equity")
            if isinstance(margins, dict) and "data" in margins:
                margins = margins["data"]

            available = margins.get("available", {})

            cash = available.get("live_balance")
            print(f"Fetch capital now : {cash}")
            if cash is not None:
                return float(cash)

            return self.logger.get_last_capital()

        except Exception as e:
            print(
                "Failed to fetch live capital from Kite:",
                e
            )

            return self.logger.get_last_capital()

    def sync_capital(self):
        if self.live_trading:
            self.capital = self._fetch_live_capital()
        print(f"Synced capital: {self.capital:.2f}")
        return self.capital

    def _get_current_price(self, symbol):
        try:
            quote = kite.quote(f"NFO:{symbol}")
            quote_data = quote.get(f"NFO:{symbol}", {})
            price = quote_data.get("last_price")
            if price is None:
                price = quote_data.get("last_price")
            return float(price) if price is not None else None
        except Exception as e:
            print(
                f"Failed to fetch current price for {symbol}:",
                e
            )
            return None

    def _calculate_qty(self, current_price, symbol):
        try:
            from data.shared import risk_manager
            return risk_manager.get_quantity(
                self.capital,
                current_price,
                symbol
            )
        except Exception as e:
            print(
                f"Failed to calculate quantity for {symbol}:",
                e
            )
            return 0

    # =========================
    # BUY
    # =========================
    def buy(
        self,
        underlying,
        symbol,
        details
        ):
        print(f"INSIDE BUY : {symbol}")
        now = datetime.now()
        order_id = None
        current_min = (
            now.hour * 60
            + now.minute
        )

        # Do not buy after 1:30 PM
        if current_min > (13 * 60):

            return

        # already exists
        if symbol in self.positions:
            print(f"SYMBOL NOT IN POSITIONS BUY : {symbol}")
            return

        current_price = self._get_current_price(symbol)
        if current_price is None:
            print(f"CURRENT PRICE IS NONE FOR {symbol}")
            return

        if self.live_trading:
            self.sync_capital()

        qty = self._calculate_qty(current_price, symbol)
        if qty <= 0:
            print(f"Quantity is 0 for {symbol}, skipping buy")
            return

        now = datetime.now()
        details["entry_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.trade_details[symbol] = details
        self.already_traded.add(underlying)

        print(
            "BUY START:",
            symbol,
            underlying,
            "qty=",
            qty,
            "avg_price=",
            current_price,
            "capital_before=",
            self.capital,
            "details=",
            details
        )
        
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

                latest = order_history[-1]


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

            buy_cost = (
                actual_avg_price
                * filled_qty
            )

            if buy_cost > self.capital:
                print(
                    f"⚠️ INSUFFICIENT CAPITAL FOR {symbol}: "
                    f"need {buy_cost:.2f}, have {self.capital:.2f}"
                )
                return

            self.capital -= buy_cost
        else:
            self.positions[symbol] = (
                current_price
            )

            self.quantity[symbol] = qty

            buy_cost = (
                current_price
                * qty
            )

            if buy_cost > self.capital:
                print(
                    f"⚠️ INSUFFICIENT CAPITAL FOR {symbol}: "
                    f"need {buy_cost:.2f}, have {self.capital:.2f}"
                )
                return

            self.capital -= buy_cost

        print(
            "BUY COMPLETE:",
            symbol,
            "qty=",
            self.quantity[symbol],
            "avg_price=",
            self.positions[symbol],
            "capital_after=",
            self.capital,
            "positions=",
            list(self.positions.keys())
        )

        self.logger.log_event(
            event="BUY",
            symbol=symbol,
            side="BUY",
            price=self.positions[symbol],
            qty=self.quantity[symbol],
            capital=self.capital,
            entry=self.positions[symbol],
            entry_time=details.get("entry_time"),
            exit_price="",
            pnl=None,
            vwap=details.get("vwap"),
            atr=details.get("atr_percent"),
            strength=details.get("candle_strength"),
            atr_ratio=details.get("atr_ratio"),
            volume_ratio=details.get("volume_ratio"),
            distance_from_vwap=details.get("distance_from_vwap"),
            details=str(details),
            order_id=order_id,
        )

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
        details
        ):
        print("About to sell trade", details)
        order_id = None

        if symbol not in self.positions:
            print(f"SYMBOL NOT IN POSITIONS SELL : {symbol}")
            return

        entry = self.positions[symbol]

        qty = self.quantity[symbol]
        print(
            "SELL START:",
            symbol,
            "entry=",
            entry,
            "qty=",
            qty,
            "capital_before=",
            self.capital,
            "entry_time=",
            details.get("entry_time"),
            "trade_details=",
            details
        )

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

                latest = order_history[-1]

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
        vwap = details.get('vwap')
        atr_percent = details.get('atr_percent')
        strength = details.get('candle_strength')
        atr_ratio = details.get('atr_ratio')
        volume_ratio = details.get('volume_ratio')
        distance_from_vwap = details.get('distance_from_vwap')
        proceeds = (
            price
            * qty
        )
        if self.live_trading:
            self.sync_capital()
        else:
            self.capital += proceeds
        self.realized_pnl += pnl
        print(
            "SELL COMPLETE:",
            symbol,
            "price=",
            price,
            "pnl=",
            pnl,
            "capital_after=",
            self.capital
        )
        self.logger.log_event(
            event="SELL",
            symbol=symbol,
            side="SELL",
            price=price,
            qty=qty,
            capital=self.capital,
            entry=entry,
            entry_time=details.get("entry_time"),
            exit_price=price,
            pnl=pnl,
            vwap=vwap,
            atr=atr_percent,
            strength=strength,
            atr_ratio=atr_ratio,
            volume_ratio=volume_ratio,
            distance_from_vwap=distance_from_vwap,
            details=str(details),
            order_id=order_id,
        )
        print("About to log trade with details:", details)
        self.logger.log_trade(
            order_id,
            symbol,
            entry,
            details.get("entry_time"),
            price,
            qty,
            pnl,
            self.capital,
            vwap,
            atr_percent,
            strength,
            atr_ratio,
            volume_ratio,
            distance_from_vwap
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

    
