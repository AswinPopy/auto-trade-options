from utils.trade_logger import TradeLogger

class PaperBroker:

    def __init__(self, capital):

        self.capital = capital

        self.positions = {}
        self.quantity = {}

        self.realized_pnl = 0

        self.logger = TradeLogger()

    def buy(self, symbol, price, qty):

        self.positions[symbol] = price
        self.quantity[symbol] = qty

    def sell(self, symbol, price, qty):

        if symbol in self.positions:

            entry = self.positions[symbol]

            pnl = (price - entry) * qty

            self.logger.log_trade(
                symbol=symbol,
                entry=entry,
                exit_price=price,
                qty=qty,
                pnl=pnl
            )
            
            self.realized_pnl += pnl

            del self.positions[symbol]
            del self.quantity[symbol]