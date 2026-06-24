from utils.trade_logger import (
    TradeLogger
)
import time
import threading
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
        self.stop_loss_order_ids = {}
        self.trade_details = {}
        self.already_traded = set()
        self.pending_orders = {}
        self.completed_order_updates = {}
        self._pending_lock = threading.Lock()

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

    def _register_order_update(self, order_id, update):
        if not order_id or not update:
            return

        order_id = str(order_id)
        status = update.get("status")
        event_to_set = None

        with self._pending_lock:
            pending = self.pending_orders.get(order_id)
            if pending is None:
                self.completed_order_updates[order_id] = update
                return

            pending["status"] = status
            pending["average_price"] = float(update.get("average_price") or 0)
            pending["filled_quantity"] = int(update.get("filled_quantity") or 0)
            pending["update"] = update

            if status in ["COMPLETE", "REJECTED", "CANCELLED"]:
                if status == "COMPLETE" and pending.get("symbol"):
                    self.order_ids[pending["symbol"]] = order_id
                event_to_set = pending["event"]
        
        if event_to_set:
            event_to_set.set()

    def on_order_update(self, ws, data):
        order_id = data.get("order_id") or data.get("orderId")
        if order_id is None:
            return

        print(
            f"📣 Order update received: {order_id} {data.get('status')}"
        )
        self._register_order_update(order_id, data)

    def _wait_for_order_update(self, order_id, symbol=None, timeout=30):
        if order_id is None:
            return None

        order_id = str(order_id)
        with self._pending_lock:
            if order_id in self.completed_order_updates:
                return self.completed_order_updates.pop(order_id)

            event = threading.Event()
            self.pending_orders[order_id] = {
                "event": event,
                "symbol": symbol,
                "status": None,
                "average_price": None,
                "filled_quantity": 0,
                "update": None,
            }

        finished = event.wait(timeout)

        with self._pending_lock:
            pending = self.pending_orders.pop(order_id, None)

        if not finished or pending is None:
            return None

        return pending.get("update") or pending

    def get_position_qty(self, symbol):
        try:
            positions = kite.positions()
            print(f"Positions : {positions}")
            for pos in positions["net"]:
                if pos["tradingsymbol"] == symbol:
                    return int(pos["quantity"])
            print("Kite position return 0")
            return 0

        except Exception as e:
            print(f"Failed to get position qty: {e}")
            return None
    
    def _get_current_price(self, symbol):
        try:
            quote = kite.quote(f"NFO:{symbol}")
            quote_data = quote.get(f"NFO:{symbol}", {})
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

            print(f"Current price for quantity : {current_price}")
            print(f"total capital for quantity : {self.capital}")
            print(f"symbol for quantity : {symbol}")
            
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

    def _get_stop_loss_price(self, entry_price):
        if entry_price is None:
            return None

        entry_price = float(entry_price)
        if entry_price <= 0:
            return None

        return round(entry_price * .80, 2)

    def _place_stop_loss_order(self, symbol, qty, entry_price):
        if not self.live_trading:
            return None

        stop_loss_price = self._get_stop_loss_price(entry_price)
        if stop_loss_price is None:
            return None

        try:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=symbol,
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=qty,
                product=kite.PRODUCT_MIS,
                order_type=kite.ORDER_TYPE_SLM,
                trigger_price=stop_loss_price,
            )
            self.stop_loss_order_ids[symbol] = order_id
            print(f"🛑 Stop-loss order placed for {symbol} at {stop_loss_price}")
            return order_id
        except Exception as e:
            print(f"Failed to place stop-loss order for {symbol}: {e}")
            return None

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
                kite.ORDER_TYPE_MARKET,

                market_protection=-1
            )

            print(
                f"LIVE BUY ORDER : "
                f"{order_id}"
            )

            order_info = self._wait_for_order_update(
                order_id,
                symbol=symbol,
                timeout=15
            )

            if order_info is None:
                print(
                    f"⚠️ Order update timeout for {order_id}, fetching order history"
                )
                try:
                    order_history = kite.order_history(order_id)
                except Exception as e:
                    print(f"Could not fetch order history: {e}")
                    order_history = []
                latest = order_history[-1] if order_history else {}
            else:
                latest = order_info

            status = latest.get("status")
            if status == "COMPLETE":
                self.trade_details[symbol] = details
                self.already_traded.add(underlying)
                self.order_ids[symbol] = order_id
                actual_avg_price = float(latest.get("average_price") or 0)
                sl_order_id = self._place_stop_loss_order(symbol, qty, actual_avg_price)
                if sl_order_id is None:
                    print("WARNING: No stop loss placed")
            elif status in ["REJECTED", "CANCELLED"]:
                print(
                    f"❌ ORDER {status}"
                )
                return
            else:
                try:
                    kite.cancel_order(
                        variety=kite.VARIETY_REGULAR,
                        order_id=order_id
                    )
                except Exception as e:
                    print(
                        f"Cancel failed: {e}"
                    )

                print(
                    f"❌ BUY ORDER ACTIVE: {status}"
                )

                return

            

            filled_qty = int(
                latest.get("filled_quantity") or qty
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

            self.positions[symbol] = (
                actual_avg_price
            )

            self.quantity[symbol] = (
                filled_qty
            )

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
            daily_slope=details.get("daily_slope"),
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
        price = None
        exit_details = details if isinstance(details, dict) else {}

        if self.live_trading:
            
            max_attempts = 3
            actual_exit_price = None

            for attempt in range(max_attempts):
                position_qty = self.get_position_qty(symbol)

                if position_qty is None:
                    print("Could not verify position quantity")
                    return

                if position_qty <= 0:
                    print("Position already closed")
                    return

                order_id = kite.place_order(

                    variety=kite.VARIETY_REGULAR,

                    exchange=kite.EXCHANGE_NFO,

                    tradingsymbol=symbol,

                    transaction_type=
                    kite.TRANSACTION_TYPE_SELL,

                    quantity=position_qty,

                    product=kite.PRODUCT_MIS,

                    order_type=
                    kite.ORDER_TYPE_MARKET,
                    market_protection=-1
                )

                print(
                    f"LIVE SELL ORDER : "
                    f"{order_id}"
                )

                order_info = self._wait_for_order_update(
                    order_id,
                    symbol=symbol,
                    timeout=60
                )

                if order_info is None:
                    current_qty = self.get_position_qty(symbol)

                    if current_qty is None:
                        print("Could not verify current position quantity")
                        return

                    if current_qty <= 0:
                        sl_order_id = self.stop_loss_order_ids.get(symbol)

                        if sl_order_id:
                            try:
                                kite.cancel_order(
                                    variety=kite.VARIETY_REGULAR,
                                    order_id=sl_order_id
                                )
                                self.stop_loss_order_ids.pop(symbol, None)
                            except Exception as e:
                                print(f"Could not cancel SL for {symbol}: {e}")

                        try:
                            order_history = kite.order_history(order_id)
                        except Exception as e:
                            print(f"Could not fetch order history: {e}")
                            order_history = []

                        complete_order = next(
                            (
                                o for o in reversed(order_history)
                                if o.get("status") == "COMPLETE"
                            ),
                            None
                        )

                        if complete_order:
                            actual_exit_price = float(
                                complete_order.get("average_price") or 0
                            )
                        else:
                            actual_exit_price = self._get_current_price(symbol)

                        if actual_exit_price is None:
                            print("Could not determine exit price")
                            return
                        qty = position_qty
                        break

                    print(
                        f"⚠️ Sell order update timeout for {order_id}, fetching order history"
                    )

                    try:
                        order_history = kite.order_history(order_id)
                    except Exception as e:
                        print(f"Could not fetch order history: {e}")
                        order_history = []
                    latest = order_history[-1] if order_history else {}
                else:
                    latest = order_info

                status = latest.get("status")
                if status == "COMPLETE":
                    actual_exit_price = float(latest.get("average_price") or 0)
                    qty = int(latest.get("filled_quantity") or qty)
                    sl_order_id = self.stop_loss_order_ids.get(symbol)

                    if sl_order_id:
                        try:
                            kite.cancel_order(
                                variety=kite.VARIETY_REGULAR,
                                order_id=sl_order_id
                            )
                            self.stop_loss_order_ids.pop(symbol, None)
                        except Exception as e:
                            print(
                                f"Could not cancel SL for {symbol}: {e}"
                            )
                    break
                elif status in ["REJECTED", "CANCELLED"]:
                    print(
                        f"Sell attempt {attempt + 1} failed. "
                        f"Order={order_id} "
                        f"Status={status}"
                    )

                    continue
                else:
                    print(
                        f"Exit order still active: {status}"
                    )
                    return
                
            else:
                print(
                    "❌ SELL NOT FILLED"
                )
                return

            price = actual_exit_price   
        else:
            price = exit_details.get("exit_price") or exit_details.get("price")
            if price is None:
                price = details if not isinstance(details, dict) else None

            if price is None:
                print(
                    "❌ No exit price provided for paper sell"
                )
                return

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
            daily_slope=details.get("daily_slope"),
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
            distance_from_vwap,
            details.get("daily_slope")
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

    
