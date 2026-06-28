from datetime import date

from utils.strike_steps import (
    get_strike_step
)
import math


def get_monthly_nse_expiry(
    year=None,
    month=None
):
    today = date.today()

    if year is None:
        year = today.year

    if month is None:
        month = today.month

    return date(year, month, 26)


def get_expiry_symbol_month(
    reference_date=None
):
    if reference_date is None:
        reference_date = date.today()

    expiry_year = reference_date.year
    expiry_month = reference_date.month

    # if reference_date.day > 25:
    #     expiry_month = expiry_month % 12 + 1
    #     if expiry_month == 1:
    #         expiry_year += 1

    expiry_date = get_monthly_nse_expiry(
        expiry_year,
        expiry_month
    )

    return expiry_date.strftime("%d%b").upper()


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

    expiry = get_expiry_symbol_month()

    return (
        f"{stock}"
        f"{expiry}"
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

    expiry = get_expiry_symbol_month()

    return (
        f"{stock}"
        f"{expiry}"
        f"{strike}PE"
    )

