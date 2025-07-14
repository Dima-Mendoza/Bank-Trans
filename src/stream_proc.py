import asyncio
import json
from datetime import datetime, time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from models import Transaction

class FraudDetector:
    @staticmethod
    def analyze(tx: Transaction) -> dict:
        """Анализирует транзакцию по базовым правилам"""
        alerts = []
        
        # Правило 1: Крупные суммы
        if (tx.currency == "RUB" and tx.amount > 100_000) or \
           (tx.currency in ["USD", "EUR"] and tx.amount > 10_000):
            alerts.append("HIGH_AMOUNT")
        
        # Правило 2: Подозрительные валюты
        crypto_currencies = ["XMR", "BTC", "USDT"]
        if tx.currency in crypto_currencies:
            alerts.append("CRYPTO_CURRENCY")
        
        # Правило 3: Ночные операции
        if tx.timestamp.time() < time(6, 0) or tx.timestamp.time() > time(23, 59):
            alerts.append("NIGHT_OPERATION")
        
        # Правило 4: Частые микротранзакции
        if tx.microtransactions_count and tx.microtransactions_count > 15:
            alerts.append("MICROTRANSACTIONS_FLOOD")

        return {
            "is_suspicious": bool(alerts),
            "alerts": alerts,
            "risk_score": len(alerts) * 25
        }

async def create_topic_if_not_exists():
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        # Получаем список топиков (синхронно)
        topics = producer.client.cluster.topics()
        if "transactions" not in topics:
            print("Создаю топик transactions...")
            # Это асинхронный вызов
            await producer.client.create_topic("transactions", 1, 1)
    finally:
        await producer.stop()

async def process_transactions():
    await create_topic_if_not_exists()
    
    consumer = AIOKafkaConsumer(
        "transactions",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="fraud-detection-v1",
        request_timeout_ms=3000,
        session_timeout_ms=10000,
        heartbeat_interval_ms=3000
    )
    
    await consumer.start()
    print("Успешно подключено к Kafka")
    print("Подписка на тему: transactions")
    
    try:
        async for msg in consumer:
            try:
                tx_data = msg.value
                print(f"Получена транзакция: {tx_data['id']}")
                
                # Конвертируем строку времени в datetime
                if 'timestamp' in tx_data:
                    tx_data['timestamp'] = datetime.fromisoformat(tx_data['timestamp'])
                
                tx = Transaction(**tx_data)
                result = FraudDetector.analyze(tx)
                
                if result["is_suspicious"]:
                    print(f"""
                    🚨 Подозрительная транзакция [Риск: {result['risk_score']}%]
                    ID: {tx.id}
                    Сумма: {tx.amount} {tx.currency}
                    Время: {tx.timestamp}
                    Причины: {", ".join(result['alerts'])}
                    """)
                    
            except json.JSONDecodeError as e:
                print(f"Неверный JSON: {e} | Данные: {msg.value}")
            except Exception as e:
                print(f"Ошибка обработки: {e}")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
    finally:
        await consumer.stop()
        print("Обработчик остановлен")

if __name__ == "__main__":
    asyncio.run(process_transactions())