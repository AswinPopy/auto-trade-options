LOT_SIZE = 550


class RiskManager:

    def get_quantity(
        self,
        capital,
        option_price
    ):

        max_amount = (
            capital * 0.5
        )

        lot_cost = (
            option_price
            * LOT_SIZE
        )

        if lot_cost <= 0:
            return 0

        lots = int(
            max_amount
            / lot_cost
        )

        lots = max(lots, 1)

        return lots * LOT_SIZE