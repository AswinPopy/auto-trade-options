import csv
import os
from datetime import datetime

from config import CAPITAL

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
                    "Order ID",
                    "Symbol",
                    "Entry",
                    "Exit",
                    "Quantity",
                    "PnL",
                    "Capital",
                    "VWAP",
                    "ATR",
                    "Strength",
                    "ATR Ratio",
                    "Volume Ratio"
                ])

    def log_trade(
        self,
        order_id,
        symbol,
        entry,
        exit_price,
        qty,
        pnl,
        capital,
        vwap,
        atr,
        strength,
        atr_ratio,
        volume_ratio
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
                order_id,
                symbol,
                entry,
                exit_price,
                qty,
                round(pnl, 2),
                round(capital, 2),
                vwap,
                atr,
                strength,
                atr_ratio,
                volume_ratio
            ])

    def get_last_capital(self, default_capital=CAPITAL):
        if not os.path.exists(self.file):
            return default_capital

        last_capital = default_capital

        with open(self.file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                capital_value = row.get("Capital")
                if not capital_value:
                    continue

                try:
                    capital_float = float(capital_value)
                except ValueError:
                    continue

                if capital_float > 0:
                    last_capital = capital_float

        return last_capital