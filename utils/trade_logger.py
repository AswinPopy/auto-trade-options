import csv
import os
import threading
import traceback
import uuid
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
        "Entry Time",
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

    EVENT_HEADER = [
        "Date",
        "Time",
        "OrderId",
        "EventId",
        "Event",
        "Symbol",
        "Side",
        "Price",
        "Quantity",
        "Remaining Capital",
        "Entry",
        "Entry Time",
        "Exit",
        "PnL",
        "vwap",
        "atr_percent",
        "strength",
        "atr_ratio",
        "volume_ratio",
        "distance_from_vwap",
        "Details",
    ]

    def __init__(self):
        self.file = Path(__file__).resolve().parent.parent / "trade_log.csv"
        self.event_file = Path(__file__).resolve().parent.parent / "trade_event_log.csv"
        self.lock = threading.Lock()
        self._ensure_header()
        self._ensure_event_header()

    def _ensure_header(self):
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self._write_rows(self.file, [self.HEADER])

    def _ensure_event_header(self):
        if not self.event_file.exists():
            self.event_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_rows(self.event_file, [self.EVENT_HEADER])

    def _write_rows(self, file_path, rows):
        with self.lock:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
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
        entry_time,
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
            self._write_rows(self.file, [
                [
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S"),
                    order_id,
                    symbol,
                    entry,
                    entry_time,
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

    def log_event(
        self,
        event,
        symbol,
        side,
        price,
        qty,
        capital,
        entry,
        entry_time,
        exit_price,
        pnl,
        vwap,
        atr,
        strength,
        atr_ratio,
        volume_ratio,
        distance_from_vwap,
        details=None,
        order_id=None,
    ):
        try:
            event_id = uuid.uuid4().hex
            self._write_rows(self.event_file, [
                [
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S"),
                    order_id,
                    event_id,
                    event,
                    symbol,
                    side,
                    price,
                    qty,
                    round(capital, 2) if capital is not None else None,
                    entry,
                    entry_time,
                    exit_price,
                    round(pnl, 2) if pnl is not None else None,
                    vwap,
                    atr,
                    strength,
                    atr_ratio,
                    volume_ratio,
                    distance_from_vwap,
                    details,
                ]
            ])
        except Exception as e:
            print(f"Error logging event: {e}")
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