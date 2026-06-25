import sys
import types

fake_kiteconnect = types.ModuleType("kiteconnect")


class DummyKiteConnect:
    def __init__(self, *args, **kwargs):
        pass

    def set_access_token(self, *args, **kwargs):
        pass


fake_kiteconnect.KiteConnect = DummyKiteConnect
sys.modules.setdefault("kiteconnect", fake_kiteconnect)

from broker.paper_broker import PaperBroker


class DummyLogger:
    def __init__(self):
        self.events = []
        self.trades = []

    def log_event(self, **kwargs):
        self.events.append(kwargs)

    def log_trade(self, *args, **kwargs):
        self.trades.append((args, kwargs))


def test_get_stop_loss_price_for_long_option():
    broker = PaperBroker.__new__(PaperBroker)

    assert broker._get_stop_loss_price(100.0) == 80.0
    assert broker._get_stop_loss_price(0.0) is None


def test_sell_logs_and_clears_position_when_already_closed():
    broker = PaperBroker.__new__(PaperBroker)
    broker.live_trading = True
    broker.positions = {"TEST": 100.0}
    broker.quantity = {"TEST": 2}
    broker.capital = 10000.0
    broker.realized_pnl = 0.0
    broker.stop_loss_order_ids = {}
    broker.logger = DummyLogger()
    broker.sync_capital = lambda: 10000.0

    broker.get_position_qty = lambda symbol: 0
    broker._get_current_price = lambda symbol: 105.0

    broker.sell("TEST", {"entry_time": "2024-01-01 09:30:00", "exit_price": 105.0})

    assert broker.logger.events
    assert broker.logger.trades
    assert "TEST" not in broker.positions
    assert "TEST" not in broker.quantity


def test_reconcile_closed_positions_logs_manual_sell():
    broker = PaperBroker.__new__(PaperBroker)
    broker.live_trading = True
    broker.positions = {"TEST": 100.0}
    broker.quantity = {"TEST": 2}
    broker.capital = 10000.0
    broker.realized_pnl = 0.0
    broker.stop_loss_order_ids = {}
    broker.trade_details = {"TEST": {"entry_time": "2024-01-01 09:30:00", "exit_price": 105.0}}
    broker.logger = DummyLogger()
    broker.sync_capital = lambda: 10000.0

    broker.get_position_qty = lambda symbol: 0
    broker._get_current_price = lambda symbol: 105.0

    broker.reconcile_closed_positions()

    assert broker.logger.events
    assert broker.logger.trades
    assert "TEST" not in broker.positions
    assert "TEST" not in broker.quantity
