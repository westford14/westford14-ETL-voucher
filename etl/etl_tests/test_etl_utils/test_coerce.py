import pytest 

import pandas as pd 

from etl_utils.coerce import coerce_missing_total_orders


def test_coerce_types():
    with pytest.raises(TypeError):
        coerce_missing_total_orders(x=10)
    
    with pytest.raises(TypeError):
        coerce_missing_total_orders(x={"x": 10})


def test_coerce_values():
    mapped = coerce_missing_total_orders("")
    assert pd.isnull(mapped)

    mapped = coerce_missing_total_orders("10")
    assert mapped == 10 

    mapped = coerce_missing_total_orders("10.0")
    assert mapped == 10
