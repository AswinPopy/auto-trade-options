class RiskManager:

    def __init__(self, lot_size_map=None):
        self._lot_size_map = lot_size_map or {}
        self._default_lot_size = 0

    def get_quantity(
        self,
        capital,
        option_price,
        symbol=None
    ):

        if capital is None:
            print(f"Capital is None : {capital}")
            return 0

        capital = float(capital)

        if capital <= 0:
            print(f"Capital less than 0 : {capital}")
            return 0

        if option_price is None or option_price <= 0:
            print("option price None : -- Riskmanager")
            return 0

        lot_size = self.get_lot_size(symbol)

        max_amount = capital * 0.5
        lot_cost = option_price * lot_size

        if lot_cost <= 0:
            print(f"lot cost less than 0 : {lot_cost}")
            return 0

        if max_amount < lot_cost:
            print(f"max amount : {max_amount} less than total cost : {lot_cost}")
            return 0

        lots = int(max_amount / lot_cost)

        #return max(lots, 1) * lot_size
        print(f"returning lot size : {lot_size}")
        return lot_size
    
    def get_lot_size(self, symbol):
        if not symbol:
            return self._default_lot_size

        return self._lot_size_map.get(symbol, self._default_lot_size)

    def set_lot_size_map(self, lot_size_map):
        if not isinstance(lot_size_map, dict):
            return

        self._lot_size_map = lot_size_map
