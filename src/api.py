from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import TransactionDB


from .db import get_session
from .crud import get_all_transactions
from .models import Transaction

app = FastAPI(title="BankTrans API", version="1.0")


@app.get("/transactions", response_model=List[Transaction])
def list_transactions(limit: int = 100, db: Session = Depends(get_session)):
    return db.query(TransactionDB).order_by(TransactionDB.timestamp.desc()).all()

