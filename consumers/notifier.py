import aio_pika
import asyncio
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_HOST, RABBITMQ_EXCHANGE


async def connect_with_retries(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            conn = await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
            print("✅ Connected to RabbitMQ")
            return conn
        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed: {e}")
            await asyncio.sleep(delay)
    print("❌ Failed to connect to RabbitMQ after retries.")
    sys.exit(1)


async def handle_notifier():
    conn = await connect_with_retries()
    channel = await conn.channel()
    exchange = await channel.declare_exchange(RABBITMQ_EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("notifier_queue")
    await queue.bind(exchange, routing_key="file.validated")
    await queue.bind(exchange, routing_key="file.infected")
    await queue.bind(exchange, routing_key="file.indexed")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                event_data = json.loads(message.body)
                print(f"[Notifier] Received Event: {event_data['event']} for {event_data['file_name']}")


if __name__ == "__main__":
    asyncio.run(handle_notifier())
