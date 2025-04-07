import pika
import os
import time

rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_USER", "disney")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "magicpass")

# Wait to ensure RabbitMQ is ready
time.sleep(10)

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='disney.queue', durable=True)

message = "🎢 Welcome aboard the Disney queue!"
channel.basic_publish(exchange='',
                      routing_key='disney.queue',
                      body=message)

print(f" [x] Sent '{message}'")
connection.close()