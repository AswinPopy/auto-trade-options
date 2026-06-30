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
            execution_queue.qsize(),
            "Capital:",
            getattr(broker, "capital", None),
            "Positions:",
            list(broker.positions.keys())
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

            if broker.live_trading:
                broker.sync_capital()

            print(
                "About to add to execution queue with details:",
                details,
                "capital:",
                broker.capital
            )
            details["underlying_entry"] = current_price
            execution_queue.put({
                "underlying": symbol,
                "symbol": option_symbol,
                "details": details
            })
            print(
                "Enqueued execution order:",
                symbol,
                "->",
                option_symbol,
                "queue size=",
                execution_queue.qsize(),
                "already_traded=",
                broker.already_traded
            )
        except Exception as e:
            print(f"Error in strategy worker for {symbol} : {e}")
            traceback.print_exc()
        finally:
            strategy_queue.task_done()

def execution_worker():

    while True:
        try:
            print(
                "Execution worker waiting; queue size=",
                execution_queue.qsize(),
                "positions=",
                len(broker.positions),
                "capital=",
                broker.capital
            )
            order = execution_queue.get(
                timeout=1
            )
            print(
                "Execution worker received order; queue size after get=",
                execution_queue.qsize()
            )
            underlying = order["underlying"]
            if underlying in broker.already_traded:
                print(f"Already traded {underlying}, skipping order")
                execution_queue.task_done()
                continue
            symbol = order["symbol"]
            print(f"EXECUTION WORKER SYMBOL : {symbol}")
            details = order["details"]
            details['underlying'] = underlying
            print("EXECUTION WORKER BUY")
            broker.buy(
                underlying,
                symbol,
                details
            )
            print(f"EXECUTION WORKER BUY COMPLETE : {symbol}")

            execution_queue.task_done()

        except Empty:
            pass
        except Exception as e:
            print(f"Error in execution worker: {e}")
            traceback.print_exc()


def exit_worker():

    while True:
        broker.reconcile_closed_positions()

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

            should_exit, atr = (
                exit_manager.should_exit(
                    position
                )
            )

            if should_exit:
                print(f"EXITING {position} at price {current}")
                details = broker.trade_details.get(
                    position,
                    {}
                )
                details['atr'] = atr
                broker.sell(
                    position,
                    details
                )
                del broker.trade_details[position]
                exit_manager.clear_position(
                    position
                )

        time.sleep(1)



