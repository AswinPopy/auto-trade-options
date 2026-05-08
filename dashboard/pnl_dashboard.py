import os


class PnLDashboard:

    def __init__(self, broker):
        self.broker = broker

    def render(self, current_prices):


        print("\n===== LIVE PnL DASHBOARD =====\n")

        realized = self.broker.realized_pnl

        unrealized = self.get_unrealized_pnl(current_prices)

        total = realized + unrealized

        print(f"Realized PnL   : {realized:.2f}")
        print(f"Unrealized PnL : {unrealized:.2f}")
        print(f"TOTAL PnL      : {total:.2f}")

        print("\n===== OPEN POSITIONS =====\n")

        if not self.broker.positions:
            print("No open CE positions")
        else:

            for symbol, entry in self.broker.positions.items():

                qty = self.broker.quantity[symbol]

                current = current_prices.get(symbol, entry)

                pnl = (current - entry) * qty

                print(
                    f"{symbol} | "
                    f"Entry: {entry:.2f} | "
                    f"Current: {current:.2f} | "
                    f"Qty: {qty} | "
                    f"PnL: {pnl:.2f}"
                )

        print("\n==============================\n")

    def get_unrealized_pnl(self, current_prices):

        pnl = 0

        for symbol in self.broker.positions:

            entry = self.broker.positions[symbol]

            qty = self.broker.quantity[symbol]

            current = current_prices.get(symbol, entry)

            pnl += (current - entry) * qty

        return pnl