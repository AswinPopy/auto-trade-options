import os


class PnLDashboard:

    def __init__(self, broker):

        self.broker = broker

    def render(self, prices):

        print("\n===== OPEN POSITIONS =====\n")

        if not self.broker.positions:

            print("No open positions")

        else:

            for symbol, entry in self.broker.positions.items():

                qty = self.broker.quantity[symbol]

                current = prices.get(
                    symbol,
                    entry
                )

                pnl = (
                    (current - entry)
                    * qty
                )

                print(
                    f"{symbol:<25}\n"
                    f"ENTRY: {entry:<10.2f}\n"
                    f"CURRENT: {current:<10.2f}\n"
                    f"QTY: {qty:<8}\n"
                    f"PnL: {pnl:.2f}"
                )

        print("\n==============================\n")