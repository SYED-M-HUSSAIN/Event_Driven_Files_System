import aio_pika
import asyncio
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_HOST, RABBITMQ_EXCHANGE
from shared.schemas import FileUploadedEvent, FileValidatedEvent


async def connect_with_retries(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            return await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"[Validator] Retry {attempt + 1}: RabbitMQ connection failed – {e}")
            await asyncio.sleep(delay)
    print("[Validator] Could not connect to RabbitMQ.")
    sys.exit(1)


async def handle_validator():
    conn = await connect_with_retries()
    channel = await conn.channel()
    exchange = await channel.declare_exchange(RABBITMQ_EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("validator_queue", durable=True)
    await queue.bind(exchange, routing_key="file.uploaded")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    event_data = json.loads(message.body)
                    file_event = FileUploadedEvent(**event_data)
                    print(f"[Validator] Validating {file_event.file_name}")

                    # Example validation check based on file extension
                    valid = file_event.file_name.endswith('.txt')
                    validated = FileValidatedEvent(file_name=file_event.file_name, valid=valid)

                    # Publish validation result to the exchange
                    await exchange.publish(
                        aio_pika.Message(body=validated.model_dump_json().encode()),
                        routing_key="file.validated"
                    )

                except Exception as e:
                    print(f"[Validator] Error processing message: {e}")


if __name__ == "__main__":
    asyncio.run(handle_validator())
