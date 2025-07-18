from sqlalchemy.orm import Session
from .models import Transaction, TransactionDB

def save_transaction(tx: Transaction, db: Session, is_suspicious: bool = False, alerts: list[str] = None, risk_score: int = 0):
    db_tx = TransactionDB(
        id=tx.id,
        amount=tx.amount,
        currency=tx.currency,
        timestamp=tx.timestamp,
        microtransactions_count=tx.microtransactions_count,
        ip=tx.ip,
        is_suspicious=is_suspicious,
        alerts=alerts or [],
        risk_score=risk_score
    )
    db.add(db_tx)
    db.commit()


def get_all_transactions(db: Session, limit: int = 100) -> list[Transaction]:
    rows = db.query(TransactionDB).order_by(TransactionDB.timestamp.desc()).limit(limit).all()
    return [Transaction.model_validate(row.__dict__) for row in rows]
