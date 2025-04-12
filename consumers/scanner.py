import aio_pika
import asyncio
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_EXCHANGE
from shared.schemas import FileUploadedEvent, FileInfectedEvent
from shared.common import  connect_with_retries

async def handle_scanner():
    conn = await connect_with_retries()
    channel = await conn.channel()
    exchange = await channel.declare_exchange(RABBITMQ_EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("scanner_queue", durable=True)
    await queue.bind(exchange, routing_key="file.uploaded")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    event_data = json.loads(message.body)
                    file_event = FileUploadedEvent(**event_data)
                    print(f"[Scanner] Scanning {file_event.file_name}")

                    # Example of file infection detection
                    infected = "virus" in file_event.file_name
                    infected_event = FileInfectedEvent(file_name=file_event.file_name, infected=infected)

                    # Publish the infected event to the exchange
                    await exchange.publish(
                        aio_pika.Message(body=infected_event.model_dump_json().encode()),
                        routing_key="file.infected"
                    )

                except Exception as e:
                    print(f"[Scanner] Error processing message: {e}")


if __name__ == "__main__":
    asyncio.run(handle_scanner())
