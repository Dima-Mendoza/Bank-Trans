from loguru import logger
import os

os.makedirs("logs", exist_ok=True)

logger.remove()
logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="10 days",
    level="INFO",
    encoding="utf-8",
    enqueue=True
)
