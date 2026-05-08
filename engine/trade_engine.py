class TradeEngine:

    def __init__(self, broker):
        self.broker = broker

    def process(self, symbol, price, signal):

        # ENTRY
        if signal == "BUY":

            if symbol not in self.broker.positions:

                self.broker.buy(symbol, price)

                print(f"🟢 BUY CE {symbol} @ {price}")

        # EXIT
        elif signal == "SELL":

            if symbol in self.broker.positions:

                self.broker.sell(symbol, price)

                print(f"🔴 EXIT CE {symbol} @ {price}")