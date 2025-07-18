import asyncio
import sys
import os
from dotenv import load_dotenv

# Добавляем src в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.local')
load_dotenv(env_path)

from src.alert_sender import MailtrapAlertSender

async def test_send():
    alert_sender = MailtrapAlertSender()
    await alert_sender.send_alert(
        {
            'id': 'TEST_123',
            'amount': 150000,
            'currency': 'RUB',
            'timestamp': '2025-07-15 14:30:00',
            'ip': '192.168.1.100'
        },
        ['HIGH_AMOUNT', 'NIGHT_OPERATION'],
        75
    )
    print("SMTP_USER:", os.getenv("SMTP_USER"))
    print("SMTP_PASSWORD:", "***" if os.getenv("SMTP_PASSWORD") else "NOT SET")
    print("Тестовое письмо отправлено")

asyncio.run(test_send())