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
        symbol,
        entry,
        exit_price,
        qty,
        pnl
    ):

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
                symbol,
                entry,
                exit_price,
                qty,
                round(pnl, 2)
            ])