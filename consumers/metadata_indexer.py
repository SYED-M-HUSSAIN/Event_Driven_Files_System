import aio_pika
import asyncio
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_EXCHANGE
from shared.schemas import FileUploadedEvent, FileIndexedEvent
from shared.common import  connect_with_retries

async def handle_indexer():
    """Main logic for handling the indexer."""
    conn = await connect_with_retries()
    channel = await conn.channel()
    exchange = await channel.declare_exchange(RABBITMQ_EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("indexer_queue", durable=True)
    await queue.bind(exchange, routing_key="file.uploaded")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    event_data = json.loads(message.body)
                    file_event = FileUploadedEvent(**event_data)
                    print(f"[Indexer] Indexing {file_event.file_name}")

                    # Metadata extraction (for example, file size and path)
                    metadata = {
                        "size": os.path.getsize(file_event.file_path),
                        "path": file_event.file_path
                    }
                    indexed_event = FileIndexedEvent(file_name=file_event.file_name, metadata=metadata)

                    # Publish the indexed event to the exchange
                    await exchange.publish(
                        aio_pika.Message(body=indexed_event.model_dump_json().encode()),
                        routing_key="file.indexed"
                    )

                except Exception as e:
                    print(f"[Indexer] Error processing message: {e}")


if __name__ == "__main__":
    asyncio.run(handle_indexer())
