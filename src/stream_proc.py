import asyncio
import json
from aiokafka import AIOKafkaConsumer
from models import Transaction

# 1. Измените порты на 9092 (стандартный для Redpanda)
BOOTSTRAP_SERVERS = ['localhost:9092']  # Используйте один порт вместо списка

TOPIC = "transactions"

async def main():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="mvp-consumer-group",
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        # 2. Добавьте таймауты для обработки проблем подключения
        request_timeout_ms=3000,
        session_timeout_ms=10000,
        heartbeat_interval_ms=3000
    )

    try:
        await consumer.start()
        print(f"Successfully connected to {BOOTSTRAP_SERVERS}")
        print(f"Subscribed to topic: {TOPIC}")
        
        async for msg in consumer:
            try:
                raw_json = msg.value.decode("utf-8")
                tx = Transaction.model_validate_json(raw_json)
                print("Processed:", tx.model_dump())
                
                # 3. Добавьте обработку транзакции
                await process_transaction(tx)
                
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e} | Raw message: {msg.value}")
            except Exception as e:
                print(f"Processing error: {e}")
                
    except Exception as e:
        print(f"Kafka connection error: {e}")
    finally:
        await consumer.stop()
        print("Consumer stopped")

async def process_transaction(tx: Transaction):
    """Дополнительная обработка транзакции"""
    # Здесь можно добавить:
    # - Валидацию через rule engine
    # - Запись в БД
    # - Отправку уведомлений
    pass

if __name__ == "__main__":
    asyncio.run(main())