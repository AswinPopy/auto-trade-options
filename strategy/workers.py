from queue import Empty
from data.queues import (
strategy_queue,
execution_queue
)

from data.shared import (
live_prices,
strategy,
broker,
risk_manager,
qty_manager,
exit_manager
)

from market.option_selector import (
    get_ce_symbol,
    get_pe_symbol
)


def strategy_worker():
    while True:
        symbol = strategy_queue.get()

        try:

            signal, details = (
                strategy.generate_signal(
                    symbol
                )
            )

            if signal is None:
                continue

            current_price = (
                live_prices.get(symbol)
            )

            print(f"Checked price : {details.get('current_price')} || Current price : {current_price}")

            if current_price is None:
                print("CURRENT PRICE IS NONE")
                continue

            if len(broker.positions) >= 1:
                print("BROKER POSITION EXIST")
                continue

            if signal == "BUY_CE":

                option_symbol = (
                    get_ce_symbol(
                        symbol,
                        current_price
                    )
                )

            elif signal == "BUY_PE":

                option_symbol = (
                    get_pe_symbol(
                        symbol,
                        current_price
                    )
                )

            else:
                print("ELSE CONTINUE")
                continue
            print(f"OPTION SYM : {option_symbol}")
            option_price = (
                live_prices.get(
                    option_symbol
                )
            )

            if option_price is None:
                print("OPTION PRICE IS NONE")
                print("Option symbol in live prices", option_symbol in live_prices)
                print("Live prices", live_prices.keys())
                continue

            qty = (
                risk_manager.get_quantity(
                    broker.capital,
                    option_price
                )
            )

            execution_queue.put({
                "symbol": option_symbol,
                "qty": qty,
                "details": details
            })

        finally:
            strategy_queue.task_done()

def execution_worker():

    while True:
        try:
            order = execution_queue.get(
                timeout=1
            )
            details = order.get('details', {})
            symbol = order["symbol"]
            print(f"EXECUTION WORKER SYMBOL : {symbol}")
            qty = order["qty"]

            execution = (
                qty_manager
                .estimate_buy_cost(
                    symbol,
                    qty
                )
            )
            print("EXECUTION WORKER BUY")
            broker.buy(
                symbol,
                execution["avg_price"],
                execution["filled_qty"],
                details
            )

            execution_queue.task_done()

        except Empty:
            pass

        # =========================
        # EXIT CHECKS
        # =========================

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
                    current
                )
            )

            qty = broker.quantity[
                position
            ]

            if should_exit:

                execution = (
                    qty_manager
                    .estimate_sell_value(
                        position,
                        qty
                    )
                )
                details = broker.trade_details.get(
                    position,
                    {}
                )
                broker.sell(
                    position,
                    execution["avg_price"],
                    details
                )
                del broker.trade_details[position]
                exit_manager.clear_position(
                    position
                )



