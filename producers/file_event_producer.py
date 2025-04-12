import pika
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.config import RABBITMQ_HOST, RABBITMQ_QUEUE

def publish_file_event(filename):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=filename
    )
    connection.close()
