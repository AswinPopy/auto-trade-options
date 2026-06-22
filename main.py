import sys
import copy
import threading
from broker.kite_session import kite
from config import UNDERLYING

from data.queues import (
    strategy_queue
)

from utils.strike_steps import (
    get_strike_step
)

from datetime import datetime
from kiteconnect import (
    KiteTicker
)

from config import (
    API_KEY,
    ACCESS_TOKEN
)

from strategy.workers import (
    strategy_worker,
    execution_worker,
    exit_worker,
    monitor
)

sys.stdout.reconfigure(
    encoding="utf-8"
)

threading.Thread(
    target=monitor,
    daemon=True
).start()

threading.Thread(
    target=strategy_worker,
    daemon=True
).start()

threading.Thread(
    target=execution_worker,
    daemon=True
).start()

threading.Thread(
    target=exit_worker,
    daemon=True
).start()

# =====================================
# INIT
# =====================================

from data.shared import (
live_prices,
broker,
candle_engine,
risk_manager
)


watchlist = copy.deepcopy(UNDERLYING)

token_to_symbol = {}

symbol_to_token = {}


# =========================
# NSE STOCKS
# =========================
nse_instruments = kite.instruments(
    "NSE"
)

for i in nse_instruments:

    token = i["instrument_token"]

    symbol = i["tradingsymbol"]

    if symbol not in UNDERLYING:
        continue
    
    token_to_symbol[token] = symbol

    symbol_to_token[symbol] = token


# =========================
# NFO OPTIONS
# =========================

nfo_instruments = kite.instruments(
    "NFO"
)

for i in nfo_instruments:

    token = i["instrument_token"]

    symbol = i["tradingsymbol"]
    if not any(

        symbol.startswith(stock)

        for stock in watchlist
    ):

        continue
        
    token_to_symbol[token] = symbol
    symbol_to_token[symbol] = token

lot_size_map = {
    item["tradingsymbol"]: item["lot_size"]
    for item in nfo_instruments
    if (
        "tradingsymbol" in item
        and "lot_size" in item
    )
}


risk_manager.set_lot_size_map(lot_size_map)

# =====================================
# GET SYMBOL
# =====================================
def get_symbol(token):

    return token_to_symbol.get(
        token
    )


def market_close_exit():

    now = datetime.now()

    current_minutes = (
        now.hour * 60
        + now.minute
    )

    # 2:45 PM
    exit_time = (
        14 * 60
        + 45
    )

    return (
        current_minutes
        >= exit_time
    )

# =====================================
# TICKS
# =====================================
def on_ticks(ws, ticks):

    global watchlist
    
    if market_close_exit():

        print(
            "⛔ Market Closing..."
        )

        print(
            "MARKET CLOSE EXIT"
        )

        for position in list(
            broker.positions.keys()
        ):

            current = live_prices.get(
                position
            )

            if current is None:
                continue

            broker.sell(
                position,
                {
                    "exit_price": current,
                    "entry_time": broker.trade_details.get(
                        position,
                        {}
                    ).get("entry_time")
                }
            )

        print(
            "✅ All Positions Closed"
        )

        ws.close()

        return

    for tick in ticks:

        token = tick[
            "instrument_token"
        ]
        
        symbol = get_symbol(token)

        price = tick[
            "last_price"    
        ]

        live_prices[symbol] = price

        if symbol is None or symbol not in UNDERLYING:
            continue

        volume = tick['last_traded_quantity']
        
        completed = (
            candle_engine.update_tick(
                symbol,
                price,
                volume
            )
        )

        if completed:
            strategy_queue.put(symbol)

        

def get_current_price(symbol):

    quote = kite.ltp(f"NSE:{symbol}")

    return quote[f"NSE:{symbol}"]["last_price"]

# =====================================
# CONNECT
# =====================================
def on_connect(ws, response):

    global watchlist

    for stock in UNDERLYING:
        current_price = (
            get_current_price(stock)
        )

        stock_watchlist = (
            build_watchlist(
                stock,
                current_price
            )
        )

        watchlist.extend(
            stock_watchlist
        )

    print("WATCH LIST", watchlist) 

    tokens = [

        symbol_to_token[s]

        for s in watchlist

        if s in symbol_to_token
    ]

    print("SUBSCRIBED SYMBOLS")

    for t in tokens:
        print(token_to_symbol[t])

    ws.subscribe(tokens)

    ws.set_mode(
        ws.MODE_FULL,
        tokens
    )

    print("✅ Connected")



def get_atm(price, step=10):
    return round(price / step) * step

def build_watchlist(
    stock,
    current_price
):

    # strike gap
    step = get_strike_step(stock)

    atm = int(get_atm(
        current_price,
        step
    ))

    strikes = [
        atm - (3 * step),
        atm - (2 * step),
        atm - step,
        atm,
        atm + step,
        atm + (2 * step),
        atm + (3 * step),
    ]

    watchlist = [stock]

    expiry = "26JUN"

    for strike in strikes:

        watchlist.append(
            f"{stock}{expiry}"
            f"{strike}CE"
        )

        watchlist.append(
            f"{stock}{expiry}"
            f"{strike}PE"
        )

    return watchlist


print("ACCESS TOKEN:", ACCESS_TOKEN)
print("API KEY:", API_KEY)
# =====================================
# START
# =====================================
kws = KiteTicker(
    API_KEY,
    ACCESS_TOKEN
)

kws.on_ticks = on_ticks

kws.on_connect = on_connect

print(
    "🚀 Starting..."
)

kws.connect()