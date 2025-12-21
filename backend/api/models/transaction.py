from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from uuid import uuid4

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    long: float = Field(..., ge=-180, le=180)
    distance_from_home: float = Field(..., ge=0)
    city: Optional[str] = None
    state: Optional[str] = None

class CustomerHistory(BaseModel):
    avg_amount: float = Field(..., gt=0)
    std_amount: Optional[float] = None
    usual_hours: List[int] = Field(..., min_items=0, max_items=24) # allow empty
    transaction_count: int = Field(..., ge=0)

class TransactionInput(BaseModel):
    transaction_id: Optional[str] = None
    amount: float = Field(..., gt=0, le=100000)
    merchant: str = Field(..., min_length=1, max_length=100)
    category: str
    time: str # ISO String
    location: Location
    customer_id: str
    customer_history: Optional[CustomerHistory] = None
    
    @validator('transaction_id', pre=True, always=True)
    def set_transaction_id(cls, v):
        return v or f"tx_{uuid4().hex[:12]}"
