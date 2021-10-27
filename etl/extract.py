import argparse
import json
import logging
import os

import pandas as pd

from etl_utils.mapping import frequency_segment, recency_segment
from etl_utils.coerce import coerce_missing_total_orders

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_parquet_clean(filepath: str) -> pd.DataFrame:
    """
    Reads the parquet file from a filepath and returns back
    mapped and cleaned columns.

    :param filepath: (str) path to the parquet file
    :return: (pd.DataFrame) cleaned pd.DataFrame
    """
    if not isinstance(filepath, str):
        raise TypeError(f"filepath must be of type str not {type(filepath)}")
    if not os.path.exists(filepath):
        raise ValueError(f"filepath - {filepath} does not exist")
    columns = {
        "timestamp": pd.to_datetime,
        "country_code": str,
        "last_order_ts": pd.to_datetime,
        "first_order_ts": pd.to_datetime,
        "total_orders": coerce_missing_total_orders,
    }

    logger.info(f"reading in parquet file -- {filepath}")
    df = pd.read_parquet(filepath, engine="fastparquet")

    logger.info("subsetting to just Peru")
    df = df[df["country_code"].isin(["Peru"])]

    for col, met in columns.items():
        logger.info(f"parsing column - {col}")
        df[col] = df[col].apply(met)
    return df


def create_dataset(df: pd.DataFrame) -> None:
    """ """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be of type pd.DataFrame not {type(df)}")
    logger.info(f"len of df pre-drop of NaNs -- {len(df)}")
    cleaned = df[~pd.isnull(df).any(axis=1)]
    logger.info(f"len of df post-drop of NaNs - {len(cleaned)}")

    logger.info("creating the time diff column")
    cleaned["time_diff"] = (
        (cleaned["timestamp"] - cleaned["last_order_ts"])
        .astype("timedelta64[D]")
        .apply(int)
    )

    logger.info("mapping voucher amount back to int")
    cleaned["voucher_amount"] = cleaned["voucher_amount"].apply(int)

    logger.info("mapping to frequency and recency segments")
    cleaned["total_orders"] = cleaned["total_orders"].apply(int)
    cleaned["frequent_segment"] = cleaned["total_orders"].apply(frequency_segment)
    cleaned["recency_segment"] = cleaned["time_diff"].apply(recency_segment)

    logger.info("final cleaning of nulls")
    cleaned = cleaned[["voucher_amount", "frequent_segment", "recency_segment"]]
    cleaned = cleaned[~pd.isnull(cleaned).any(axis=1)]

    logger.info("saving to JSON blobs")
    rec_seg = cleaned.groupby(["recency_segment"], as_index=False)[
        "voucher_amount"
    ].agg(lambda x: x.value_counts().index[0])
    freq_seg = cleaned.groupby(["frequent_segment"], as_index=False)[
        "voucher_amount"
    ].agg(lambda x: x.value_counts().index[0])

    freq_dict = freq_seg.set_index("frequent_segment").to_dict()["voucher_amount"]
    for x in ["0-4", "5-13", "13-37"]:
        if x not in freq_dict:
            freq_dict[x] = 0

    logger.info("saving freq_segment.json")
    with open("data/freq_segment.json", "w") as f:
        json.dump(freq_dict, f)

    rec_dict = rec_seg.set_index("recency_segment").to_dict()["voucher_amount"]
    for x in ["30-60", "60-90", "90-120", "120-180", "180+"]:
        if x not in rec_dict:
            rec_dict[x] = 0

    logger.info("saving rec_segment.json")
    with open("data/rec_segment.json", "w") as f:
        json.dump(rec_dict, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="the file that you want to extract from")
    args = parser.parse_args()
    file_to_extract = args.file
    df = read_parquet_clean(file_to_extract)
    create_dataset(df)
