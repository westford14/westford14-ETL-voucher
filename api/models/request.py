from pydantic import BaseModel, validator


class VoucherRequest(BaseModel):
    """
    Request model for the api/v1/voucher endpoint
    """

    customer_id: int
    country_code: str
    last_order_ts: str
    first_order_ts: str
    total_orders: int
    segment_name: str

    @validator("country_code", pre=True, always=True)
    def check_country_code(cls, v):
        if v != "Peru":
            raise ValueError(f"this API is only concerned with vouchers for Peru")
        return v

    @validator("segment_name", pre=True, always=True)
    def check_segment_names(cls, v):
        allowed_segments = ["frequent_segment", "recency_segment"]
        if v not in allowed_segments:
            raise ValueError(
                f"segment_name: {v} not understood -- only 'frequent_segment' and 'recency_segment' allowed"
            )
        return v


class VoucherResponse(BaseModel):
    """
    Response model for the api/v1/voucher endpoint
    """

    voucher: int
