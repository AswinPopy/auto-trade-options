from kiteconnect import KiteConnect, KiteTicker

from config import API_KEY, ACCESS_TOKEN

from data.candle_engine import CandleEngine
from strategy.strategy_engine import StrategyEngine
from engine.broker import PaperBroker
from engine.trade_engine import TradeEngine
from dashboard.pnl_dashboard import PnLDashboard


kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)


# ---------------- INIT ----------------
candle_engine = CandleEngine()
broker = PaperBroker(100000)
strategy = StrategyEngine(candle_engine)
trade_engine = TradeEngine(broker)
dashboard = PnLDashboard(broker)


token_to_symbol = {}
symbol_to_token = {}

instruments = kite.instruments("NSE")

for i in instruments:
    token_to_symbol[i["instrument_token"]] = i["tradingsymbol"]
    symbol_to_token[i["tradingsymbol"]] = i["instrument_token"]


latest_prices = {}


def get_symbol(token):
    return token_to_symbol.get(token)


def on_ticks(ws, ticks):

    global latest_prices

    for tick in ticks:

        token = tick["instrument_token"]
        price = tick["last_price"]

        symbol = get_symbol(token)

        if not symbol:
            continue

        latest_prices[symbol] = price

        completed = candle_engine.update_tick(symbol, price)

        if completed:
            signal = strategy.generate_signal(symbol)

            trade_engine.process(symbol, price, signal)

    dashboard.render(latest_prices)


def on_connect(ws, response):

    WATCHLIST = ["HDFCBANK"]

    tokens = [symbol_to_token[s] for s in WATCHLIST]

    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)

    print("Connected")


kws = KiteTicker(API_KEY, ACCESS_TOKEN)

kws.on_ticks = on_ticks
kws.on_connect = on_connect

print("Starting...")

kws.connect()