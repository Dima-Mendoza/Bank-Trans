from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, validates

from .db import Base
from .encryption import encrypt, decrypt


class TransactionDB(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    microtransactions_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    ip_encrypted = Column("ip", String, nullable=True)  # РЕАЛЬНОЕ поле
    is_suspicious = Column(Boolean, default=False)
    alerts = Column(ARRAY(String))
    risk_score = Column(Integer)

    @property
    def ip(self) -> Optional[str]:
        if self.ip_encrypted:
            try:
                return decrypt(self.ip_encrypted)
            except Exception:
                return None
        return None

    @ip.setter
    def ip(self, value: Optional[str]):
        self.ip_encrypted = encrypt(value) if value else None



class Transaction(BaseModel):
    id: str
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    microtransactions_count: Optional[int] = None
    ip: Optional[str] = None
    is_suspicious: Optional[bool] = False
    alerts: Optional[List[str]] = []
    risk_score: Optional[int] = 0

    model_config = ConfigDict(extra='ignore')
