import pika

def get_interface(host, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="router_info")

    channel.queue_bind(queue="router_info", exchange="jobs", routing_key="check_interfaces")
    channel.basic_publish(exchange="jobs", routing_key="check_interfaces", body=body)
    connection.close()

def set_config(host, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="set_router")

    channel.queue_bind(queue="set_router", exchange="jobs", routing_key="set_config")
    channel.basic_publish(exchange="jobs", routing_key="set_config", body=body)
    connection.close()
