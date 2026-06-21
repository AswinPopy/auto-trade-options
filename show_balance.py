import json

from broker.kite_session import kite
from config import LIVE_TRADING
from utils.trade_logger import TradeLogger


def fetch_live_balance():
    margins = kite.margins("equity")
    if isinstance(margins, dict) and "data" in margins:
        margins = margins["data"]
    return margins


def print_balance():
    print(f"LIVE_TRADING={LIVE_TRADING}")
    if not LIVE_TRADING:
        print("LIVE_TRADING is False. Set LIVE_TRADING=True in config.py to read Zerodha live balance.")
        logger = TradeLogger()
        print("Last logged capital:", logger.get_last_capital())
        return

    try:
        balance = fetch_live_balance()
        print(balance)
    except Exception as exc:
        print("Failed to fetch live balance from Kite:", exc)
        return

    print("=== Zerodha Live Balance ===")
    if isinstance(balance, dict):
        available_balance = balance.get('available').get('live_balance')
        print(f"Available balance is : {available_balance}")
    else:
        print(balance)


if __name__ == "__main__":
    print_balance()
