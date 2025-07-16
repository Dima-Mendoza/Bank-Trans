from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class TransactionDB(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    microtransactions_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)


class Transaction(BaseModel):
    id: str
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    microtransactions_count: Optional[int] = None
    ip: Optional[str] = None

    model_config = ConfigDict(extra='ignore')
