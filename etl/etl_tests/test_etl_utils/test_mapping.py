import pytest

import pandas as pd 

from etl_utils.mapping import frequency_segment, recency_segment 

def test_frequency_segment_type():
    with pytest.raises(TypeError):
        frequency_segment(orders="10")

    with pytest.raises(TypeError):
        frequency_segment(orders={"x": 10})


def test_frequency_segment_values():
    seg = frequency_segment(1)
    assert seg == "0-4"

    seg = frequency_segment(12)
    assert seg == "5-13"

    seg = frequency_segment(24)
    assert seg == "13-37"

    seg = frequency_segment(1000)
    assert pd.isnull(seg)
    

def test_recency_segment_type():
    with pytest.raises(TypeError):
        recency_segment(days="10")

    with pytest.raises(TypeError):
        recency_segment(days={"x": 10})


def test_recency_segment_values():
    seg = recency_segment(10)
    assert pd.isnull(seg)

    seg = recency_segment(34)
    assert seg == "30-60"

    seg = recency_segment(85)
    assert seg == "60-90"

    seg = recency_segment(112)
    assert seg == "90-120"

    seg = recency_segment(1000)
    assert seg == "180+"
