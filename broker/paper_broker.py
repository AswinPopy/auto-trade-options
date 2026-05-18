from utils.trade_logger import (
    TradeLogger
)
from datetime import datetime
class PaperBroker:

    def __init__(self):

        self.logger = TradeLogger()

        self.capital = self.logger.get_last_capital()

        self.positions = {}

        self.quantity = {}

        self.realized_pnl = 0


    # =========================
    # BUY
    # =========================
    def buy(self, symbol, price, qty):
        now = datetime.now()

        current_min = (
            now.hour * 60
            + now.minute
        )
        # Do not buy after 02.30 PM
        if current_min > (13*60 + 30):
            return
        
        # already exists
        if symbol in self.positions:
            return

        self.positions[symbol] = price

        self.quantity[symbol] = qty

        print(
            f"🟢 BOUGHT "
            f"{symbol} @ {price}"
        )

    # =========================
    # SELL
    # =========================
    def sell(self, symbol, price):

        if symbol not in self.positions:
            return

        entry = self.positions[symbol]

        qty = self.quantity[symbol]

        pnl = (
            (price - entry)
            * qty
        )

        self.realized_pnl += pnl

        self.capital += pnl
        self.logger.log_trade(
            symbol,
            entry,
            price,
            qty,
            pnl
        )
        print(
            f"🔴 SOLD "
            f"{symbol} @ {price}"
        )

        print(
            f"PnL = {pnl:.2f}"
        )

        del self.positions[symbol]

        del self.quantity[symbol]