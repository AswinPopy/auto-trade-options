LOT_SIZE = 550


class RiskManager:

    def get_quantity(
        self,
        capital,
        option_price
    ):

        if capital is None:
            return 0

        capital = float(capital)

        if capital <= 0:
            return 0

        if option_price is None or option_price <= 0:
            return 0

        max_amount = (
            capital * 0.5
        )

        lot_cost = (
            option_price
            * LOT_SIZE
        )

        if lot_cost <= 0:
            return 0

        if max_amount < lot_cost:
            return 0

        lots = int(
            max_amount
            / lot_cost
        )

        return max(lots, 1) * LOT_SIZE