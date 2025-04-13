import pika
import os
import time
import psycopg2
from psycopg2 import sql
import logging
import json
from prometheus_client import start_http_server, Counter

# Prometheus metrics
messages_received = Counter("consumer_messages_received_total", "Total messages received from RabbitMQ")
postgres_errors = Counter("consumer_postgres_errors_total", "PostgreSQL insert errors")

# Start Prometheus HTTP server
start_http_server(8000)  # Exposes /metrics

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Env vars
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_USER", "disney")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "magicpass")

pg_host = os.getenv("POSTGRES_HOST", "postgresql")
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
pg_db   = os.getenv("POSTGRES_DB", "disney_events")

def ensure_table_exists(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            type TEXT,
            timestamp DOUBLE PRECISION,
            location TEXT,
            payload JSONB
        )
    """)
    conn.commit()
    cur.close()

def callback(ch, method, properties, body):
    message_raw = body.decode()
    logging.info(f"✔ Received message: {message_raw}")
    messages_received.inc()  # ← increment here, as soon as message is received

    try:
        message = json.loads(message_raw)
        conn = psycopg2.connect(
            host=pg_host,
            database=pg_db,
            user=pg_user,
            password=pg_pass
        )
        ensure_table_exists(conn)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (type, timestamp, location, payload) VALUES (%s, %s, %s, %s)",
            (message["type"], message["timestamp"], message["location"], json.dumps(message["payload"]))
        )
        conn.commit()
        cur.close()
        conn.close()
        logging.info("→ Message saved to PostgreSQL")
    except Exception as e:
        logging.error(f"PostgreSQL error: {e}")
        postgres_errors.inc()  # ← increment error counter if insert fails

# Continuous consumer loop
while True:
    try:
        logging.info("~ Connecting to RabbitMQ...")
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue='shipboard-events', durable=True)

        logging.info("* Waiting for messages. To exit press CTRL+C")
        channel.basic_consume(queue='shipboard-events', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        logging.warning(f"RabbitMQ connection error: {e}. Retrying in 5 seconds...")
        time.sleep(5)