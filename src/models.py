from datetime import datetime 
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class Transaction(BaseModel):
    id: str
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    microtransactions_count: Optional[int] = None
    ip: Optional[str] = None
    
    model_config = ConfigDict(extra='ignore')