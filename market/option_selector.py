from utils.strike_steps import (
    get_strike_step
)
import math

EXPIRY = "26MAY"

def get_atm_strike(
    stock,
    price,
    option_type
):
    print(f"About to get strike step for : {stock}")
    step = get_strike_step(
        stock
    )

    # CE -> lower strike
    if option_type == "CE":

        return int(
            math.floor(
                price / step
            ) * step
        )

    # PE -> higher strike
    if option_type == "PE":

        return int(
            math.ceil(
                price / step
            ) * step
        )


def get_ce_symbol(
    stock,
    price
):

    strike = get_atm_strike(
        stock,
        price,
        "CE"
    )

    return (
        f"{stock}"
        f"{EXPIRY}"
        f"{strike}CE"
    )


def get_pe_symbol(
    stock,
    price
):

    strike = get_atm_strike(
        stock,
        price,
        "PE"
    )

    return (
        f"{stock}"
        f"{EXPIRY}"
        f"{strike}PE"
    )

