import pika

def publish_message(exchange, queue, routing_key, body, host="rabbitmq"):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    print(f"[Producer] Sent message to '{queue}' (routing: {routing_key})")
    connection.close()

def get_interface(host, body):
    publish_message("jobs", "router_info", "check_interfaces", body, host)

def set_config(host, body):
    publish_message("jobs", "set_router", "set_config", body, host)
