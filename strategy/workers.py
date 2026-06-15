from queue import Empty
import traceback
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

from config import MAX_CONCURRENT_TRADES

from market.option_selector import (
    get_ce_symbol,
    get_pe_symbol
)

import time

def monitor():

    while True:

        print(
            "Strategy:",
            strategy_queue.qsize(),
            "Execution:",
            execution_queue.qsize()
        )

        time.sleep(10)

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

            if len(broker.positions) >= MAX_CONCURRENT_TRADES:
                print("BROKER POSITION FULL")
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
            print(f"OPTION PRICE : {option_price}")
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
            print("About to add to execution queue with details:", details)
            details["underlying_entry"] = current_price
            execution_queue.put({
                "underlying": symbol,
                "symbol": option_symbol,
                "qty": qty,
                "price": option_price,
                "details": details
            })
        except Exception as e:
            print(f"Error in strategy worker for {symbol} : {e}")
            traceback.print_exc()
        finally:
            strategy_queue.task_done()

def execution_worker():

    while True:
        try:
            print("Waiting for execution order...")
            order = execution_queue.get(
                timeout=1
            )
            underlying = order["underlying"]
            if underlying in broker.already_traded:
                print(f"Already traded {underlying}, skipping order")
                execution_queue.task_done()
                continue
            symbol = order["symbol"]
            print(f"EXECUTION WORKER SYMBOL : {symbol}")
            qty = order["qty"]
            price = order["price"]
            details = order["details"]
            # execution = (
            #     qty_manager
            #     .estimate_buy_cost(
            #         symbol,
            #         qty
            #     )
            # )
            print("EXECUTION WORKER BUY")
            broker.buy(
                underlying,
                symbol,
                price,
                qty,
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
            print(f"Checking exit for {position}")
            current = live_prices.get(
                position
            )

            if current is None:
                print(f"Current price for {position} is None, skipping exit check")
                continue

            should_exit = (
                exit_manager.should_exit(
                    position
                )
            )

            qty = broker.quantity[
                position
            ]

            if should_exit:
                print(f"EXITING {position} at price {current}")
                # execution = (
                #     qty_manager
                #     .estimate_sell_value(
                #         position,
                #         qty
                #     )
                # )
                details = broker.trade_details.get(
                    position,
                    {}
                )
                broker.sell(
                    position,
                    current,
                    details
                )
                del broker.trade_details[position]
                exit_manager.clear_position(
                    position
                )



