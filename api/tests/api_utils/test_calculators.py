import pytest
from datetime import datetime

from api_utils.calculators import frequency_segment, recency_segment

def test_frequency_segment_type():
    with pytest.raises(TypeError):
        frequency_segment(orders=[10]) 

    with pytest.raises(TypeError):
        frequency_segment(orders="10")

def test_frequency_values():
    assert frequency_segment(orders=2) == "0-4"
    assert frequency_segment(orders=11) == "5-13"
    assert frequency_segment(orders=20) == "13-37"
    assert frequency_segment(orders=400000) is None 

def test_recency_segment_type():
    with pytest.raises(TypeError):
        recency_segment(last_order=10)

    with pytest.raises(TypeError):
        recency_segment(last_order={"last_order": datetime.now()})
    
def test_recency_segment_value():
    time_str = "1990-10-24 00:00:00"

    assert recency_segment(time_str) == "180+"

