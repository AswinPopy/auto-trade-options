import sys
sys.stdout.reconfigure(
    encoding="utf-8"
)
import copy
from utils.strike_steps import (
    get_strike_step
)
from broker.kite_session import kite
from config import UNDERLYING
import logging
from datetime import datetime
from kiteconnect import (
    KiteTicker
)

from broker.quantity_manager import(
    QuantityManager
)

from risk.risk_manager import (
    RiskManager
)

from risk.exit_manager import (
    ExitManager
)

from config import (
    API_KEY,
    ACCESS_TOKEN
)

from data.candle_engine import (
    CandleEngine
)

from strategy.strategy_engine import (
    StrategyEngine
)

from broker.paper_broker import (
    PaperBroker
)


from market.option_selector import (
    get_ce_symbol,
    get_pe_symbol
)

# =====================================
# INIT
# =====================================

risk_manager = RiskManager(
)

candle_engine = CandleEngine()

strategy = StrategyEngine(
    candle_engine
)

broker = PaperBroker(
)

qty_manager = QuantityManager()

exit_manager = ExitManager(
    candle_engine,
    broker
)


watchlist = copy.deepcopy(UNDERLYING)

live_prices = {}

token_to_symbol = {}

symbol_to_token = {}


# =====================================
# LOAD INSTRUMENTS
# =====================================
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

        for stock in UNDERLYING
    ):

        continue
    
    token_to_symbol[token] = symbol

    symbol_to_token[symbol] = token

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

    global live_prices
    global watchlist
    
    if market_close_exit():

        logging.info(
            "⛔ Market Closing..."
        )

        logging.info(
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
                current
            )

        logging.info(
            "✅ All Positions Closed"
        )

        ws.close()

        return

    for tick in ticks:

        token = tick[
            "instrument_token"
        ]

        price = tick[
            "last_price"
        ]

        volume = tick['last_traded_quantity']
    
        symbol = get_symbol(token)

        if symbol is None:
            continue

        live_prices[symbol] = price

        if symbol not in UNDERLYING:
            continue
        
        

        completed = (
            candle_engine.update_tick(
                symbol,
                price,
                volume
            )
        )

        if completed:

            logging.info(
                "\nCANDLE CLOSED"
            )

            logging.info(completed)

            signal = (
                strategy.generate_signal(
                    symbol
                )
            )

            logging.info(
                f"SIGNAL = "
                f"{signal}"
            )

            # ==================
            # BUY CALL
            # ==================
            if signal == "BUY_CE":

                ce_symbol = (
                    get_ce_symbol(symbol, price)
                )

                if ce_symbol not in watchlist:
                    logging.info(f"CE SYMBOL : {ce_symbol} not in watch list")
                    return
                
                ce_price = (
                    live_prices.get(
                        ce_symbol
                    )
                )

                if ce_price:

                    qty = risk_manager.get_quantity(
                        broker.capital,
                        ce_price
                    )
                    execution = qty_manager.estimate_buy_cost(ce_symbol, qty)
                    if broker.positions:

                        logging.info(
                            "⛔ Existing Position Open"
                        )

                        return
                    logging.info(f"About to buy CE : {ce_symbol} for price : {ce_price} qty : {qty}")
                    broker.buy(
                        ce_symbol,
                        execution["avg_price"],
                        execution["filled_qty"]
                    )

            # ==================
            # BUY PUT
            # ==================
            elif signal == "BUY_PE":

                pe_symbol = (
                    get_pe_symbol(symbol, price)
                )

                if pe_symbol not in watchlist:
                    logging.info(f"PE SYMBOL : {pe_symbol} not in watch list")
                    return
                
                pe_price = (
                    live_prices.get(
                        pe_symbol
                    )
                )

                if pe_price:

                    qty = risk_manager.get_quantity(
                        broker.capital,
                        pe_price
                    )

                    execution = qty_manager.estimate_buy_cost(pe_symbol, qty)

                    if broker.positions:

                        logging.info(
                            "⛔ Existing Position Open"
                        )

                        return
                    logging.info(f"About to buy PE : {pe_symbol} for price : {pe_price} qty : {qty}")
                    broker.buy(
                        pe_symbol,
                        execution["avg_price"],
                        execution["filled_qty"]
                    )

        # ==========================
        # EXIT LOGIC
        # ==========================
        for position in list(
            broker.positions.keys()
        ):

            current = live_prices.get(
                position
            )

            if current is None:
                continue

            should_exit = (
                exit_manager.should_exit(
                    position,
                    current,
                    live_prices
                )
            )

            if should_exit:
                
                execution = (
                    qty_manager
                    .estimate_sell_value(
                    symbol,
                    qty
                    )
                    )
                
                broker.sell(
                    position,
                    execution["avg_price"]
                )

                exit_manager.clear_position(
                    position
                )


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
        atm - (2 * step),
        atm - step,
        atm,
        atm + step,
        atm + (2 * step)
    ]

    watchlist = [stock]

    expiry = "26MAY"

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



# =====================================
# START
# =====================================
kws = KiteTicker(
    API_KEY,
    ACCESS_TOKEN
)

kws.on_ticks = on_ticks

kws.on_connect = on_connect

logging.info(
    "🚀 Starting..."
)

kws.connect()