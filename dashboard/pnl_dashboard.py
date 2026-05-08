import os


class PnLDashboard:

    def __init__(self, broker):

        self.broker = broker

    def render(self, prices):

        os.system("clear")

        # =========================
        # LIVE PRICES
        # =========================
        print("\n===== LIVE PRICES =====\n")

        for symbol, current in prices.items():

            print(
                f"{symbol}\n"
                f"CURRENT: {current:.2f}\n"
            )

        # =========================
        # OPEN POSITIONS
        # =========================
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
                    f"{symbol}\n"
                    f"ENTRY   : {entry:.2f}\n"
                    f"CURRENT : {current:.2f}\n"
                    f"QTY     : {qty}\n"
                    f"PnL     : {pnl:.2f}\n"
                )

        print("\n==============================\n")