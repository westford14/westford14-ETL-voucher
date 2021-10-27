from typing import Optional

import numpy as np


def coerce_missing_total_orders(x: str) -> Optional[int]:
    """
    Utility function that maps "" -> np.nan and
    casts a string to an int

    :param x: (str) the value to map
    :return: (np.nan or int) the mapped value
    """
    if not isinstance(x, str):
        raise TypeError(f"x must be of type str not {type(x)}")
    if x == "":
        return np.nan
    else:
        return int(float(x))
