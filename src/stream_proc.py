import asyncio
import json
from datetime import datetime, time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .models import Transaction
from .rule_engine import fraud_engine
from .db import get_session
from .crud import save_transaction

BOOTSTRAP_SERVERS = [
    'localhost:19092',
    'localhost:10092',
    'localhost:11092',
]

async def process_transactions():
    # await create_topic_if_not_exists()
    
    consumer = AIOKafkaConsumer(
        "transactions",
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="mvp-consumer-group",
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
                # result = FraudDetector.analyze(tx)
                result = fraud_engine.analyze(tx)

                with get_session() as db:
                    save_transaction(tx, db)
                
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

# BOOTSTRAP_SERVERS = [
#     'localhost:19092',
#     'localhost:10092',
#     'localhost:11092',
# ]

# TOPIC = "transactions"


# async def main():
#     consumer = AIOKafkaConsumer(
#         TOPIC,
#         bootstrap_servers=BOOTSTRAP_SERVERS,
#         group_id="mvp-consumer-group",
#         enable_auto_commit=True,
#         auto_offset_reset="earliest",
#         # request_timeout_ms=3000,
#         # session_timeout_ms=10000,
#         # heartbeat_interval_ms=3000
#     )

#     await consumer.start()
#     print(f"Subscribed to topic: {TOPIC}")
#     try:
#         async for msg in consumer:
#             try:
#                 raw_json = msg.value.decode("utf-8")
#                 tx = Transaction.model_validate_json(raw_json)
#                 print("Processed:", tx.model_dump())

#                 # сюда потом rule engine + запись в БД
#             except Exception as e:
#                 print(f"Failed to parse message: {e}")
#     finally:
#         await consumer.stop()


# if __name__ == "__main__":
#     asyncio.run(main())
