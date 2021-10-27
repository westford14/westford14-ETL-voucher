import json
import logging
import logging.config
import os

from fastapi import FastAPI
from models.request import VoucherRequest, VoucherResponse
from api_utils.calculators import frequency_segment, recency_segment

# load in the logging configuration
try:
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
except KeyError:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.warn("running locally -- debug mode on")

# load the "database"
db = {}

if os.environ.get("TESTING") is not None:
    with open("rec_segment.json", "r") as f:
        db["recency_segment"] = json.load(f)
    with open("freq_segment.json", "r") as f:
        db["frequent_segment"] = json.load(f)
else:
    with open("data/rec_segment.json", "r") as f:
        db["recency_segment"] = json.load(f)
    with open("data/freq_segment.json", "r") as f:
        db["frequent_segment"] = json.load(f)
logger.debug("db successfully loaded")
app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict:
    """
    Health check endpoint

    Example:
        curl GET localhost:8000/healthz

    Returns:
        {"status": "ok"}
    """
    logger.debug("healthz check")
    return {"status": "ok"}


@app.post("/api/v1/voucher", response_model=VoucherResponse)
async def voucher(voucher: VoucherRequest) -> VoucherResponse:
    """
    Endpoint to gather the suggested voucher for a specified
    customer. The returned voucher value is based on either
    the time difference between a customer's last order and
    now or the number of total orders they have made.

    Example:
        {
            "customer_id": 123,
            "country_code": "Peru",
            "last_order_ts": "2018-05-03 00:00:00",
            “first_order_ts”: "2017-05-03 00:00:00",
            "total_orders": 15,
            "segment_name": "frequent_segment"
        }

    Returns:
        {
            "voucher": 2640
        }
    """
    logger.debug(f"received request for api/v1/voucher -- {voucher}")
    if voucher.segment_name == "frequent_segment":
        key = frequency_segment(int(voucher.total_orders))
    else:
        key = recency_segment(voucher.last_order_ts)
    voucher = int(db[voucher.segment_name][key])
    logger.debug(f"successfully parsed voucher amount -- {voucher}")
    return {"voucher": voucher}
