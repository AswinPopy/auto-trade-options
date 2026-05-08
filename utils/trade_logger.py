import csv
import os
from datetime import datetime


class TradeLogger:

    def __init__(self):

        self.file = "trades.csv"

        # create file with headers
        if not os.path.exists(self.file):

            with open(
                self.file,
                "w",
                newline=""
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    "date",
                    "time",
                    "symbol",
                    "entry",
                    "exit",
                    "qty",
                    "pnl"
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
                now.date(),
                now.strftime("%H:%M:%S"),
                symbol,
                entry,
                exit_price,
                qty,
                pnl
            ])