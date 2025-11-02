import time, pika

from callback import callback

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
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue="router_info", on_message_callback=callback, auto_ack=True)
    ch.start_consuming()

if __name__=='__main__':
    consume("rabbitmq")
