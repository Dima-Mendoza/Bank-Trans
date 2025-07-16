from .db import engine
from .models import TransactionDB

def create_tables():
    print("Создание таблиц в БД...")
    TransactionDB.__table__.create(bind=engine, checkfirst=True)
    print("✅ Таблица 'transactions' готова")

if __name__ == "__main__":
    create_tables()
