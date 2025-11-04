from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

def save_interface_status(ip, hostname, interfaces, routes):
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    collection = db["router_info"]

    bkk_timezone = timezone(timedelta(hours=7))
    now_bkk = datetime.now(bkk_timezone)

    router_doc = {
        "hostname": hostname,
        "ip_address": ip,
        "last_update": now_bkk.strftime("%H:%M"),
        "status": "up",
        "interfaces": interfaces,
        "routes": routes
    }

    collection.update_one(
        {"ip_address": ip},
        {"$set": router_doc},
        upsert=True
    )

    client.close()

def save_config(job_id, router_ip, int_name, new_ip, new_subnet, new_status, success):
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    router_info = db["router_info"]
    updates = db["updates"]

    updates.update_one(
        {"_id": job_id},
        {"$set": {"success": "true" if success else "failed"}},
        upsert=False
    )

    if success:
        router_info.update_one(
            {"ip_address": router_ip, "interfaces.interface": int_name}, # <--- แก้ไข: ใช้ ip_address
            {"$set": {
                "interfaces.$.ip_address": new_ip,
                "interfaces.$.subnet_mask": new_subnet,
                "interfaces.$.status": new_status.lower()
            }},
            upsert=False
        )

    print(f"[INFO] MongoDB updated for job {job_id} ({'success' if success else 'failed'})")
    client.close()