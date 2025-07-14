from datetime import datetime 
from pydantic import BaseModel, ConfigDict, Field

class Transaction(BaseModel):
    id: str
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    microtransactions_count: int | None = None
    ip: str | None = None
    
    model_config = ConfigDict(extra='ignore')