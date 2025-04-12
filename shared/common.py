import aio_pika
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_HOST

async def connect_with_retries(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            return await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"[Validator] Retry {attempt + 1}: RabbitMQ connection failed – {e}")
            await asyncio.sleep(delay)
    print("[Validator] Could not connect to RabbitMQ.")
    sys.exit(1)