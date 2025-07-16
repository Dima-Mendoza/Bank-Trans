from datetime import time
from .models import Transaction
from typing import Callable, List


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
    )
]

fraud_engine = RuleEngine(default_rules)
