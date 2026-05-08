from kiteconnect import (
    KiteConnect,
    KiteTicker
)

from risk.risk_manager import (
    RiskManager
)

from config import (
    API_KEY,
    ACCESS_TOKEN,
    CAPITAL
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

from dashboard.pnl_dashboard import (
    PnLDashboard
)

from market.option_selector import (
    get_ce_symbol,
    get_pe_symbol
)


# =====================================
# INIT
# =====================================
kite = KiteConnect(
    api_key=API_KEY
)

kite.set_access_token(
    ACCESS_TOKEN
)

risk_manager = RiskManager(
)

candle_engine = CandleEngine()

strategy = StrategyEngine(
    candle_engine
)

broker = PaperBroker(
    CAPITAL
)

dashboard = PnLDashboard(
    broker
)

UNDERLYING = "HDFCBANK"

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

    token_to_symbol[token] = symbol

    symbol_to_token[symbol] = token
# =====================================
# GET SYMBOL
# =====================================
def get_symbol(token):

    return token_to_symbol.get(
        token
    )


# =====================================
# TICKS
# =====================================
def on_ticks(ws, ticks):

    global live_prices

    for tick in ticks:

        token = tick[
            "instrument_token"
        ]

        price = tick[
            "last_price"
        ]

        volume = tick['last_traded_quantity']
        print("volume", volume)
        symbol = get_symbol(token)

        if symbol is None:
            continue

        live_prices[symbol] = price

        # ==========================
        # BUILD CANDLE ONLY
        # FOR HDFCBANK STOCK
        # ==========================
        if symbol == UNDERLYING:

            completed = (
                candle_engine.update_tick(
                    symbol,
                    price,
                    volume
                )
            )

            if completed:

                print(
                    "\nCANDLE CLOSED"
                )

                print(completed)

                signal = (
                    strategy.generate_signal(
                        UNDERLYING
                    )
                )

                print(
                    f"SIGNAL = "
                    f"{signal}"
                )

                # ==================
                # BUY CALL
                # ==================
                if signal == "BUY_CE":

                    ce_symbol = (
                        get_ce_symbol(price)
                    )

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
                      
                        if broker.positions:

                            print(
                                "⛔ Existing Position Open"
                            )

                            return
                        broker.buy(
                            ce_symbol,
                            ce_price,
                            qty
                        )

                # ==================
                # BUY PUT
                # ==================
                elif signal == "BUY_PE":

                    pe_symbol = (
                        get_pe_symbol(price)
                    )

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

                        if broker.positions:

                            print(
                                "⛔ Existing Position Open"
                            )

                            return
                        broker.buy(
                            pe_symbol,
                            pe_price,
                            qty
                        )

        # ==========================
        # EXIT LOGIC
        # ==========================
        for position in list(
            broker.positions.keys()
        ):

            entry = broker.positions[
                position
            ]

            qty = broker.quantity[
                position
            ]

            current = live_prices.get(
                position
            )

            if current is None:
                continue

            pnl = (
                (current - entry)
                * qty
            )

            # target
            if pnl >= 500:

                broker.sell(
                    position,
                    current
                )

            # stoploss
            elif pnl <= -300:

                broker.sell(
                    position,
                    current
                )

    dashboard.render(
        live_prices
    )

def get_current_price(symbol):

    quote = kite.ltp(f"NSE:{symbol}")

    return quote[f"NSE:{symbol}"]["last_price"]

# =====================================
# CONNECT
# =====================================
def on_connect(ws, response):
    
    current_price = get_current_price(
        "HDFCBANK"
    )

    WATCHLIST = build_watchlist(current_price)
    print(WATCHLIST)
    tokens = [

        symbol_to_token[s]

        for s in WATCHLIST

        if s in symbol_to_token
    ]

    ws.subscribe(tokens)

    ws.set_mode(
        ws.MODE_FULL,
        tokens
    )

    print(
        "✅ Connected"
    )


def get_strike_step(price, step=10):
    return round(price / step) * step

def build_watchlist(current_price):
    step = 10

    atm = get_strike_step(current_price, step)

    strikes = [
        atm - 20,
        atm - 10,
        atm,
        atm + 10,
        atm + 20
    ]

    watchlist = ["HDFCBANK"]

    for strike in strikes:
        watchlist.append(f"HDFCBANK26MAY{strike}CE")
        watchlist.append(f"HDFCBANK26MAY{strike}PE")

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

print(
    "🚀 Starting..."
)

kws.connect()