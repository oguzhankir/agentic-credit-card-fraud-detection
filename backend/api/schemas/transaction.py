from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union

class TransactionInput(BaseModel):
    """
    Input schema for transaction analysis.
    Matches the fields expected by feature engineering.
    """
    # Core Transaction Fields
    trans_date_trans_time: Union[datetime, str] = Field(..., description="Transaction timestamp (UTC)")
    amt: float = Field(..., gt=0, description="Transaction amount")
    merchant: str = Field(..., description="Details of merchant")
    category: str = Field(..., description="Transaction category")
    
    # Customer Fields
    dob: Union[datetime, str] = Field(..., description="Customer date of birth")
    lat: Optional[float] = Field(None, description="Customer latitude")
    long: Optional[float] = Field(None, description="Customer longitude")
    
    # Extended Fields (Explicitly requested by user)
    cc_num: Optional[int] = Field(None, description="Credit Card Number")
    first: Optional[str] = Field(None, description="First Name")
    last: Optional[str] = Field(None, description="Last Name")
    gender: Optional[str] = Field(None, description="Gender")
    street: Optional[str] = Field(None, description="Street Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip: Optional[str] = Field(None, description="Zip Code")
    city_pop: Optional[int] = Field(None, description="City Population")
    job: Optional[str] = Field(None, description="Job Title")
    trans_num: Optional[str] = Field(None, description="Transaction Number")
    unix_time: Optional[int] = Field(None, description="Unix Timestamp")
    merch_zip: Optional[str] = Field(None, description="Merchant Zip")
    
    # Merchant Fields
    merch_lat: Optional[float] = Field(None, description="Merchant latitude")
    merch_long: Optional[float] = Field(None, description="Merchant longitude")
    
    # Optional history context (if provided by upstream service)
    cust_tx_count: Optional[int] = Field(1, description="Total customer transactions")
    days_since_last_tx: Optional[float] = Field(None, description="Days since previous transaction")
    cust_avg_amt: Optional[float] = Field(None, description="Customer average transaction amount")
    cust_std_amt: Optional[float] = Field(None, description="Customer transaction standard deviation")
    
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "trans_date_trans_time": "2020-12-22 23:13:39",
                "cc_num": 2242176657877538,
                "merchant": "fraud_Jaskolski-Vandervort",
                "category": "misc_net",
                "amt": 766.38,
                "first": "Travis",
                "last": "Daniel",
                "gender": "M",
                "street": "1327 Rose Causeway Apt. 610",
                "city": "Unknown",
                "state": "Unknown",
                "zip": "00000",
                "lat": 34.6323,
                "long": -89.8855,
                "city_pop": 14462,
                "job": "Database administrator",
                "dob": "1959-03-03",
                "trans_num": "44292cbc51e37dc018ee6a988a4bc426",
                "unix_time": 1387754019,
                "merch_lat": 33.771462,
                "merch_long": -90.651342
            }
        }
