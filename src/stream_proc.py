import asyncio
import json
from datetime import datetime, time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from models import Transaction

class FraudDetector:
    @staticmethod
    def analyze(tx: Transaction) -> dict:
        alerts = []
        
        if (tx.currency == "RUB" and tx.amount > 100_000) or \
           (tx.currency in ["USD", "EUR"] and tx.amount > 10_000):
            alerts.append("HIGH_AMOUNT")
        
        crypto_currencies = ["XMR", "BTC", "USDT"]
        if tx.currency in crypto_currencies:
            alerts.append("CRYPTO_CURRENCY")
        
        if tx.timestamp.time() < time(6, 0) or tx.timestamp.time() > time(23, 59):
            alerts.append("NIGHT_OPERATION")
        
        if tx.microtransactions_count and tx.microtransactions_count > 15:
            alerts.append("MICROTRANSACTIONS_FLOOD")

        return {
            "is_suspicious": bool(alerts),
            "alerts": alerts,
            "risk_score": len(alerts) * 25
        }

async def setup_environment():
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        topics = producer.client.cluster.topics()
        if "transactions" not in topics:
            print("Создаю топик transactions...")
            await producer.client.create_topic("transactions", 1, 1)
    finally:
        await producer.stop()

async def process_transactions():
    await setup_environment()
    
    consumer = AIOKafkaConsumer(
        "transactions",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="transaction-monitoring",
        request_timeout_ms=3000,
        session_timeout_ms=10000,
        heartbeat_interval_ms=3000
    )
    
    await consumer.start()
    print("Система мониторинга запущена")
    
    try:
        async for msg in consumer:
            try:
                tx_data = msg.value
                tx_data['timestamp'] = datetime.fromisoformat(tx_data['timestamp'])
                tx = Transaction(**tx_data)
                result = FraudDetector.analyze(tx)
                
                if result["is_suspicious"]:
                    print(f"""
                    🚨 Подозрительная транзакция [Риск: {result['risk_score']}%]
                    ID: {tx.id}
                    Сумма: {tx.amount:.2f} {tx.currency}
                    Время: {tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    Причины: {", ".join(result['alerts'])}
                    """)
                    
            except Exception as e:
                print(f"Ошибка обработки: {e}")
    finally:
        await consumer.stop()
        print("Мониторинг остановлен")

if __name__ == "__main__":
    asyncio.run(process_transactions())