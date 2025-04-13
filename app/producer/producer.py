import pika
import json
import time
import random
import os
from prometheus_client import start_http_server, Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Prometheus metric
messages_sent = Counter("producer_messages_sent_total", "Total messages sent to RabbitMQ")

# Start Prometheus HTTP server
start_http_server(8000)  # /metrics exposed here

# Env vars
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Setup connection
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='shipboard-events', durable=True)

def generate_event():
    event_types = ["rfid_scan", "pos_sale", "security_alert", "training_completion"]
    event = {
        "type": random.choice(event_types),
        "timestamp": time.time(),
        "location": random.choice(["ship_1", "castaway_cay", "aulani", "wdw"]),
        "payload": {
            "id": random.randint(1000, 9999),
            "value": random.random()
        }
    }
    return event

try:
    while True:
        message = generate_event()
        channel.basic_publish(
            exchange='',
            routing_key='shipboard-events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        messages_sent.inc()  # Prometheus metric incremented here
        logging.info(f"[x] Sent: {message}")
        time.sleep(5)

except KeyboardInterrupt:
    logging.info("Shutting down producer...")
    connection.close()
except Exception as e:
    logging.error(f"Unexpected error: {e}")