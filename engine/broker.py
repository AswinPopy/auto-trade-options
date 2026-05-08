class PaperBroker:

    def __init__(self, capital):

        self.capital = capital
        self.positions = {}
        self.quantity = {}
        self.realized_pnl = 0

    def buy(self, symbol, price, qty=1):

        self.positions[symbol] = price
        self.quantity[symbol] = qty

    def sell(self, symbol, price, qty=1):

        if symbol not in self.positions:
            return

        entry = self.positions[symbol]

        pnl = (price - entry) * qty

        self.realized_pnl += pnl

        del self.positions[symbol]
        del self.quantity[symbol]