import aio_pika
import asyncio
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_EXCHANGE
from shared.common import  connect_with_retries


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
