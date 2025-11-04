import time, pika
from callback import callback_info, callback_config

def consume(host):
    for attempt in range(10):
        try:
            print(f"Connecting to RabbitMQ (try {attempt})...")
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            break
        except Exception as e:
            print(f"Failed: {e}")
            time.sleep(5)
    else:
        print("Could not connect after 10 attempts")
        exit(1)

    ch = conn.channel()

    ch.queue_declare(queue="router_info")
    ch.basic_consume(queue="router_info", on_message_callback=callback_info, auto_ack=True)

    ch.queue_declare(queue="router_config")
    ch.basic_consume(queue="router_config", on_message_callback=callback_config, auto_ack=False)

    print("[Consumer] Waiting for messages from router_info and router_config...")
    ch.start_consuming()

if __name__ == '__main__':
    consume("rabbitmq")
