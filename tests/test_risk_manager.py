import os
import tempfile
import unittest

from risk.risk_manager import RiskManager
from utils.trade_logger import TradeLogger


class RiskManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = RiskManager(lot_size_map={"TEST1234": 200})

    def test_returns_zero_when_capital_cannot_cover_one_lot(self):
        self.assertEqual(self.manager.get_quantity(1000, 50, "TEST1234"), 0)

    def test_returns_zero_for_non_positive_capital(self):
        self.assertEqual(self.manager.get_quantity(0, 50, "TEST1234"), 0)
        self.assertEqual(self.manager.get_quantity(-1000, 50, "TEST1234"), 0)

    def test_returns_one_lot_quantity_based_on_symbol_lot_size(self):
        self.assertEqual(self.manager.get_quantity(20000, 50, "TEST1234"), 200)


class TradeLoggerTests(unittest.TestCase):
    def test_ignores_negative_capital_from_previous_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "trade_log.csv")
            with open(log_path, "w", encoding="utf-8") as fh:
                fh.write(
                    "Date,Time,Order ID,Symbol,Entry,Exit,Quantity,PnL,Capital\n"
                    "2026-06-11,10:00:00,,TEST,10,9,550,-550,-168592.5\n"
                )

            logger = TradeLogger()
            logger.file = log_path
            self.assertEqual(logger.get_last_capital(), 100000)


if __name__ == "__main__":
    unittest.main()
