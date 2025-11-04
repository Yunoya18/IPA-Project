import pika
import os

def publish_message(exchange, queue, routing_key, body, host="rabbitmq"):
    user = os.getenv("RABBITMQ_DEFAULT_USER")
    pwd  = os.getenv("RABBITMQ_DEFAULT_PASS")

    creds = pika.PlainCredentials(user, pwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=creds))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=queue, durable=False)
    channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=pika.BasicProperties(delivery_mode=2))

    print(f"[Producer] Sent message to '{queue}' (routing_key='{routing_key}')")
    connection.close()


def get_interface(host, body):
    publish_message(exchange="jobs", queue="router_info", routing_key="check_interfaces", body=body, host=host)


def set_config(host, body):
    publish_message(exchange="jobs", queue="router_config", routing_key="router_update", body=body, host=host)
