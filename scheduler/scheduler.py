import time
from bson import json_util
from database import get_router_info, get_router_update
from producer import get_interface, set_config

def scheduler():
    INTERVAL = 60.0
    next_run = time.monotonic()

    while True:
        try:
            for data in get_router_info():
                body_bytes = json_util.dumps(data).encode("utf-8")
                get_interface("rabbitmq", body_bytes)

            for data in get_router_update():
                body_bytes = json_util.dumps(data).encode("utf-8")
                set_config("rabbitmq", body_bytes)

        except Exception as e:
            print(f"[Scheduler] Error: {e}")
            time.sleep(3)

        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))

if __name__ == "__main__":
    scheduler()