from bson import json_util
from router_client import get_interfaces, set_config
from database import save_interface_status, save_config

def callback_info(ch, method, props, body):
    job = json_util.loads(body.decode())

    router_ip = job["ip_address"]
    router_username = job["username"]
    router_password = job["password"]

    try:
        output_hostname, output_int, output_route = get_interfaces(router_ip, router_username, router_password)
        save_interface_status(router_ip, output_hostname, output_int, output_route)
        print(f"[INFO] Data saved for router {router_ip}")
    except Exception as e:
        print(f"[ERROR][router_info] {e}")

def callback_config(ch, method, props, body):
    job = json_util.loads(body.decode())
    job_id = None

    try:
        job_id = job["_id"] 
        
        router_ip = job["ip_router"]
        router_username = job["username"]
        router_password = job["password"]
        int_name = job["name"]
        new_ip = job["ip_address"]
        new_subnet = job["subnet_mask"]
        new_status = job["status"]

        print(f"[CONFIG] Received config job {job_id} → {router_ip} ({int_name})")

        success, output = set_config(router_ip, router_username, router_password, int_name, new_ip, new_subnet, new_status)

        save_config(job_id, router_ip, int_name, new_ip, new_subnet, new_status, success)
        print(f"[CONFIG] {'Success' if success else 'Failed'} updating {int_name} on {router_ip}")

    except Exception as e:
        print(f"[ERROR][router_config] {e}")

        if job_id:
            save_config(job_id, router_ip, int_name, new_ip, new_subnet, new_status, False) # <--- ส่ง False
