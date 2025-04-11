import pika
import os
import time

rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_USER", "disney")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "magicpass")

def callback(ch, method, properties, body):
    print(f" [✔] Received: {body.decode()}")

while True:
    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue='shipboard-events', durable=True)
        channel.basic_consume(queue='shipboard-events', on_message_callback=callback, auto_ack=True)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.basic_consume(queue='disney.queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f" [!] Connection failed: {e}. Retrying in 5s...")
        time.sleep(5)