from broker.kite_session import kite


class QuantityManager:
    def estimate_buy_cost(
        self,
        symbol,
        required_qty
        ):

        quote = kite.quote(
            f"NFO:{symbol}"
        )

        sell_depth = quote[
            f"NFO:{symbol}"
        ]["depth"]["sell"]

        remaining = required_qty

        total_cost = 0

        total_filled = 0

        for level in sell_depth:

            price = level["price"]

            available_qty = (
                level["quantity"]
            )

            take_qty = min(
                remaining,
                available_qty
            )

            total_filled += take_qty

            total_cost += (
                take_qty
                * price
            )

            remaining -= take_qty

            if remaining <= 0:
                break

        if total_filled == 0:

            return None

        avg_price = (
            total_cost
            / total_filled
        )

        return {
            "total_cost": total_cost,
            "filled_qty": total_filled,
            "avg_price": avg_price
        }

    def estimate_sell_value(
        self,
        symbol,
        required_qty
        ):

        quote = kite.quote(
            f"NFO:{symbol}"
        )

        buy_depth = quote[
            f"NFO:{symbol}"
        ]["depth"]["buy"]

        remaining = required_qty

        total_value = 0

        total_filled = 0

        for level in buy_depth:

            price = level["price"]

            available_qty = (
                level["quantity"]
            )

            take_qty = min(
                remaining,
                available_qty
            )

            total_filled += take_qty

            total_value += (
                take_qty
                * price
            )

            remaining -= take_qty

            if remaining <= 0:
                break

        if total_filled == 0:

            return None

        avg_price = (
            total_value
            / total_filled
        )

        return {
            "total_value": total_value,
            "filled_qty": total_filled,
            "avg_price": avg_price
        }
    
if __name__ == "__main__":
    symbol = "YESBANK30JUN22CE"
    print("total cost : ", QuantityManager().estimate_buy_cost(symbol, 122000))
