import pytz

from datetime import datetime
from typing import Optional


def frequency_segment(orders: int) -> Optional[str]:
    """
    Based on the total orders, calculate the segment that
    the customer falls into.

    Ex. orders = 4 -> "0-4"

    :param orders: (int) the number of orders a customer has made
    :return: (str or None) the resultant segment the customer falls into
    """
    if not isinstance(orders, int):
        raise TypeError(f"orders must be of type int not {type(orders)}")
    if orders < 0:
        return None
    elif orders < 4:
        return "0-4"
    elif orders < 13:
        return "5-13"
    elif orders < 37:
        return "13-37"
    else:
        return None


def recency_segment(last_order: str) -> Optional[str]:
    """
    Based on the last order, calculate which segment
    the customer falls into. If the requested last_order is
    a str, we will attempt to cast

    Ex. 2021-10-26 09:41:50.219696+0000 -> "180+"

    :param last_order: (datetime.date or str) the date that the last order occured at
    :return: (str or None) the resultant segment the customer falls into
    """
    if not isinstance(last_order, str):
        raise TypeError(f"last_order must be of type str not {type(last_order)}")
    if isinstance(last_order, str):
        last_order = datetime.strptime(last_order, "%Y-%m-%d %H:%M:%S")
        last_order = pytz.utc.localize(last_order)
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    days = (now - last_order).days
    if days < 30:
        return None
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
