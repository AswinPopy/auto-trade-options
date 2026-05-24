import csv
import os
from datetime import datetime

class TradeLogger:

    def __init__(self):

        self.file = "trade_log.csv"

        # create file if not exists
        if not os.path.exists(self.file):

            with open(
                self.file,
                "w",
                newline=""
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    "Date",
                    "Time",
                    "Symbol",
                    "Entry",
                    "Exit",
                    "Quantity",
                    "PnL"
                ])

    def log_trade(
        self,
        order_id,
        symbol,
        entry,
        exit_price,
        qty,
        pnl,
        vwap,
        atr,
        strength
    ):
        prev_capital = self.get_last_capital()
        new_capital = prev_capital + pnl

        now = datetime.now()
        with open(
            self.file,
            "a",
            newline=""
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                order_id,
                symbol,
                entry,
                exit_price,
                qty,
                round(pnl, 2),
                round(new_capital, 2),
                vwap,
                atr,
                strength
            ])

    def get_last_capital(self, default_capital=100000):
        if not os.path.exists(self.file):
            return default_capital

        last_capital = default_capital

        with open(self.file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Capital"):
                    last_capital = float(row["Capital"])

        return last_capital