import os


class PnLDashboard:

    def __init__(self, broker):

        self.broker = broker

    def render(self, prices):

        os.system(
            "cls" if os.name == "nt"
            else "clear"
        )

        # =========================
        # HDFC SPOT PRICE
        # =========================
        hdfc_price = prices.get(
            "HDFCBANK",
            0
        )

        print(
            "\n===== HDFC SPOT =====\n"
        )

        print(
            f"HDFCBANK : "
            f"{hdfc_price}"
        )

        # =========================
        # OPTION PRICES
        # =========================
        print(
            "\n===== OPTION PRICES =====\n"
        )

        for symbol, price in prices.items():

            # skip stock symbol
            if symbol == "HDFCBANK":
                continue

            print(
                f"{symbol:<25}"
                f"{price}"
            )

        # =========================
        # OPEN POSITIONS
        # =========================
        print(
            "\n===== OPEN POSITIONS =====\n"
        )

        if not self.broker.positions:

            print(
                "No open positions"
            )

        else:

            for symbol, entry in (
                self.broker.positions.items()
            ):

                current = prices.get(
                    symbol,
                    entry
                )

                qty = (
                    self.broker.quantity[symbol]
                )

                pnl = (
                    (current - entry)
                    * qty
                )

                print(
                    f"{symbol}\n"
                    f"ENTRY   : {entry}\n"
                    f"CURRENT : {current}\n"
                    f"QTY     : {qty}\n"
                    f"PnL     : {pnl:.2f}\n"
                )

        # =========================
        # REALIZED PNL
        # =========================
        print(
            f"REALIZED PnL : "
            f"{self.broker.realized_pnl:.2f}"
        )

        print(
            f"CAPITAL : "
            f"{self.broker.capital:.2f}"
        )
    