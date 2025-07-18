import aiosmtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))

class SimpleAlertSender:
    async def send_alert(self, tx_data: dict, reasons: list, risk_score: int):
        alert_message = f"""
        🚨 ALERT [Risk: {risk_score}%]
        ID: {tx_data['id']}
        Amount: {tx_data['amount']} {tx_data['currency']}
        Time: {tx_data['timestamp']}
        Reasons: {", ".join(reasons)}
        IP: {tx_data.get('ip', 'N/A')}
        """
        
        # Вывод в консоль
        print(alert_message)
        
        # Запись в файл
        with open("fraud_alerts.log", "a", encoding="utf-8") as f:
            f.write(alert_message + "\n")
        
        print("Alert logged to file")

class MailtrapAlertSender:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
        self.smtp_port = int(os.getenv("SMTP_PORT", 2525))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", "alerts@bank-trans.dev")
        self.receiver_email = os.getenv("RECEIVER_EMAIL", "security@example.com")

    async def send_alert(self, tx_data: dict, reasons: list, risk_score: int):
        if not all([self.smtp_user, self.smtp_password]):
            print("SMTP credentials not set. Email alerts disabled.")
            return

        # Создаем MIME-сообщение с альтернативами (текст + HTML)
        msg = MIMEMultipart('alternative')
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email
        msg["Subject"] = f"🚨 Подозрительная транзакция [Риск: {risk_score}%]"
        
        # Текстовая версия
        text_body = f"""
        ОБНАРУЖЕНА ПОДОЗРИТЕЛЬНАЯ ТРАНЗАКЦИЯ
        
        ID: {tx_data['id']}
        Сумма: {tx_data['amount']} {tx_data['currency']}
        Время: {tx_data['timestamp']}
        IP: {tx_data.get('ip', 'N/A')}
        Риск: {risk_score}%
        Причины: {", ".join(reasons)}
        
        Это сообщение из учебной системы Bank-Trans.
        """
        part1 = MIMEText(text_body.strip(), "plain", "utf-8")
        
        # HTML-версия
        html_body = f"""
        <html>
          <body>
            <h2 style="color: #d9534f;">🚨 ОБНАРУЖЕНА ПОДОЗРИТЕЛЬНАЯ ТРАНЗАКЦИЯ</h2>
            <p>Система мониторинга <b>Bank-Trans</b> обнаружила подозрительную операцию:</p>
            <ul>
              <li><b>ID транзакции:</b> {tx_data['id']}</li>
              <li><b>Сумма:</b> {tx_data['amount']} {tx_data['currency']}</li>
              <li><b>Время:</b> {tx_data['timestamp']}</li>
              <li><b>IP-адрес:</b> {tx_data.get('ip', 'N/A')}</li>
              <li><b>Уровень риска:</b> <span style="color: red;">{risk_score}%</span></li>
              <li><b>Причины:</b> {", ".join(reasons)}</li>
            </ul>
            <p><em>Это автоматическое сообщение из учебной системы мониторинга.</em></p>
          </body>
        </html>
        """
        part2 = MIMEText(html_body.strip(), "html", "utf-8")
        
        # Добавляем обе версии в сообщение
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                use_tls=False
            )
            print(f"Оповещение отправлено на {self.receiver_email}")
        except Exception as e:
            print(f"Ошибка отправки email: {str(e)}")