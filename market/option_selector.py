def get_atm_strike(price):

    return round(price / 10) * 10


def get_ce_symbol(price):

    strike = get_atm_strike(price)

    return (
        f"HDFCBANK26MAY"
        f"{strike}CE"
    )


def get_pe_symbol(price):

    strike = get_atm_strike(price)
    strike += 10
    return (
        f"HDFCBANK26MAY"
        f"{strike}PE"
    )