from fastapi import FastAPI, UploadFile
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import aio_pika
import shutil
from shared.config import RABBITMQ_HOST, RABBITMQ_EXCHANGE
from shared.schemas import FileUploadedEvent

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    conn = await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
    channel = await conn.channel()
    exchange = await channel.declare_exchange(RABBITMQ_EXCHANGE, aio_pika.ExchangeType.TOPIC)

    event = FileUploadedEvent(file_name=file.filename, file_path=file_location)
    await exchange.publish(
        aio_pika.Message(body=event.model_dump_json().encode()),
        routing_key="file.uploaded"
    )
    await conn.close()
    return {"message": "File uploaded and event published."}