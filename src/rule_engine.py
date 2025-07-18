from datetime import time, timedelta, datetime
from .models import TransactionDB, Transaction
from typing import Callable, List
from .db import get_session


class Rule:
    def __init__(self, name: str, condition: Callable[[Transaction], bool]):
        self.name = name
        self.condition = condition

    def check(self, tx: Transaction) -> bool:
        return self.condition(tx)


class RuleEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def analyze(self, tx: Transaction) -> dict:
        alerts = [rule.name for rule in self.rules if rule.check(tx)]
        return {
            "is_suspicious": bool(alerts),
            "alerts": alerts,
            "risk_score": len(alerts) * 25
        }

def check_recent_similar_transactions(ip, amount):
    with get_session() as db:
        recent = db.query(TransactionDB).filter(
            TransactionDB.ip == ip,
            TransactionDB.amount == amount,
            TransactionDB.timestamp >= datetime.utcnow() - timedelta(minutes=5)
        ).count()
        return recent > 2

def is_offshore_ip(ip):
    offshore_ranges = ["83.44.", "181.23."]
    return any(ip.startswith(prefix) for prefix in offshore_ranges)



default_rules = [
    Rule(
        "HIGH_AMOUNT",
        lambda tx: (
            (tx.currency == "RUB" and tx.amount > 300_000) or
            (tx.currency in ["USD", "EUR"] and tx.amount > 4000) or
            (tx.currency in ["BTC", "XMR"] and tx.amount > 2000)
        )
    ),
    Rule(
        "CRYPTO_CURRENCY",
        lambda tx: tx.currency in ["BTC", "XMR", "USDT"] and tx.amount > 2000
    ),
    Rule(
        "NIGHT_OPERATION",
        lambda tx: tx.timestamp.time() < time(6, 0)
    ),
    Rule(
        "MICROTRANSACTIONS_FLOOD",
        lambda tx: tx.microtransactions_count is not None and tx.microtransactions_count > 15
    ),
    Rule(
        "STRUCTURING",
        lambda tx: tx.amount in range(99000, 100001) and tx.currency == "RUB"
    ),
    Rule(
        "REPEATED_TRANSACTIONS",
        lambda tx: tx.ip and check_recent_similar_transactions(tx.ip, tx.amount)
    ),
    Rule(
        "OFFSHORE_OPERATION",
        lambda tx: tx.ip and is_offshore_ip(tx.ip)
    ),
]

fraud_engine = RuleEngine(default_rules)
