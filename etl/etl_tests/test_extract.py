import pytest 

import numpy as np 
import pandas as pd 

from extract import read_parquet_clean
from . import skip 


@pytest.fixture
def example_filepath():
    filepath = "fixtures/data.parquet.gzip"
    return filepath


def test_read_parquet_clean_type():
    with pytest.raises(TypeError):
        read_parquet_clean(filepath=10)

    with pytest.raises(TypeError):
        read_parquet_clean(filepath={"x": 10})


def test_read_parquet_path_does_not_exist():
    with pytest.raises(ValueError):
        read_parquet_clean("path/does/not/exist")


@pytest.mark.skipif(skip, reason="data file not found")
def test_read_parquet_clean_test_peru(example_filepath):
    df = read_parquet_clean(example_filepath)
    assert len(df['country_code'].value_counts()) == 1


@pytest.mark.skipif(skip, reason="data file not found")
def test_read_parquet_clean(example_filepath):
    df = read_parquet_clean(example_filepath)
    df = df[~pd.isnull(df).any(axis=1)]

    assert len(df) != 0

    column_maps = {
        "timestamp": pd.core.dtypes.dtypes.DatetimeTZDtype,
        "country_code": np.object_,
        "last_order_ts": pd.core.dtypes.dtypes.DatetimeTZDtype,
        "first_order_ts": pd.core.dtypes.dtypes.DatetimeTZDtype,
        "total_orders": np.float64,
    }

    for col, col_type in column_maps.items():
        if col == 'country_code':
            assert np.issubdtype(df[col].dtype, col_type)
        elif col =='total_orders':
            assert np.issubdtype(df[col].dtype, col_type)
        else:
            assert isinstance(df[col].dtype, col_type)
