import pika
import os
import time
import psycopg2

# Env vars
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_USER", "disney")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "magicpass")
pg_host = os.getenv("POSTGRES_HOST", "postgresql")  # service name in k8s
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
pg_db   = os.getenv("POSTGRES_DB", "disney_events")

def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [✔] Received: {message}")

    try:
        conn = psycopg2.connect(
            host=pg_host,
            database=pg_db,
            user=pg_user,
            password=pg_pass
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO events (message) VALUES (%s)", (message,))
        conn.commit()
        cur.close()
        conn.close()
        print(" [→] Saved to PostgreSQL")
    except Exception as e:
        print(f" [!] PostgreSQL error: {e}")