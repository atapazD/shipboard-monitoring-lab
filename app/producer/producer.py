import pika
import json
import time
import random
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Setup connection
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Use the same queue name as the consumer
channel.queue_declare(queue='disney.queue', durable=True)

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
            routing_key='disney.queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
        print(f"[x] Sent: {message}")
        time.sleep(5)
except KeyboardInterrupt:
    print("Shutting down producer...")
    connection.close()