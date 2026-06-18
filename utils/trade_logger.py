import csv
import os
import threading
import traceback
from datetime import datetime
from pathlib import Path

from config import CAPITAL


class TradeLogger:

    HEADER = [
        "Date",
        "Time",
        "OrderId",
        "Symbol",
        "Entry",
        "Exit",
        "Quantity",
        "PnL",
        "Capital",
        "vwap",
        "atr_percent",
        "strength",
        "atr_ratio",
        "volume_ratio",
        "distance_from_vwap",
    ]

    def __init__(self):
        self.file = Path(__file__).resolve().parent.parent / "trade_log.csv"
        self.lock = threading.Lock()
        self._ensure_header()

    def _ensure_header(self):
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self._write_rows([self.HEADER])

    def _write_rows(self, rows):
        with self.lock:
            with open(self.file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass

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
        volume_ratio,
        distance_from_vwap
    ):
        try:
            now = datetime.now()
            self._write_rows([
                [
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
                    volume_ratio,
                    distance_from_vwap,
                ]
            ])
        except Exception as e:
            print(f"Error logging trade: {e}")
            print(traceback.format_exc())

    def get_last_capital(self, default_capital=CAPITAL):
        if not self.file.exists():
            return default_capital

        last_capital = default_capital

        with open(self.file, "r", encoding="utf-8", newline="") as f:
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