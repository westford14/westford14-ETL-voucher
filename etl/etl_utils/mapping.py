import numpy as np

from typing import Optional


def frequency_segment(orders: int) -> Optional[str]:
    """
    Based on the total orders, calculate the segment that
    the customer falls into.

    Ex. orders = 4 -> "0-4"

    :param orders: (int) the number of orders a customer has made
    :return: (str or np.NaN) the resultant segment the customer falls into
    """
    if not isinstance(orders, int):
        raise TypeError(f"orders must be of type int not {type(orders)}")
    if orders < 0:
        return np.nan
    elif orders < 4:
        return "0-4"
    elif orders < 13:
        return "5-13"
    elif orders < 37:
        return "13-37"
    else:
        return np.nan


def recency_segment(days: int) -> Optional[str]:
    """
    Based on the last order, calculate which segment
    the customer falls into.

    Ex. 121 -> "180+"

    :param last_order: (int) days since last purchase
    :return: (str or np.NaN) the resultant segment the customer falls into
    """
    if not isinstance(days, int):
        raise TypeError(f"last_order must be of type int not {type(days)}")
    if days < 30:
        return np.nan
    elif days < 60:
        return "30-60"
    elif days < 90:
        return "60-90"
    elif days < 120:
        return "90-120"
    elif days < 180:
        return "120-180"
    else:
        return "180+"
