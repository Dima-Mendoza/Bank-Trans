import json
import uuid
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer

def generate_transaction():
    # 30% chance для подозрительных транзакций
    is_suspicious = random.random() < 0.3
    
    # Создаем словарь напрямую
    return {
        "id": str(uuid.uuid4()),
        "amount": random.uniform(1, 150_000),
        "currency": random.choice(["RUB", "USD", "EUR", "BTC"]),
        "timestamp": datetime.utcnow().isoformat(),  # ISO-строка
        "microtransactions_count": random.randint(1, 20) if is_suspicious else 0,
        "ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
    }

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    
    print("Генератор транзакций запущен...")
    try:
        while True:
            tx = generate_transaction()
            producer.send("transactions", tx)
            print(f"Отправлена транзакция: {tx['id']} ({tx['amount']:.2f} {tx['currency']})")
            time.sleep(random.uniform(0.5, 2))
    except KeyboardInterrupt:
        print("\nГенератор остановлен")
    finally:
        producer.close()