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


def test_get_stop_loss_price_for_long_option():
    broker = PaperBroker.__new__(PaperBroker)

    assert broker._get_stop_loss_price(100.0) == 95.0
    assert broker._get_stop_loss_price(0.0) is None
