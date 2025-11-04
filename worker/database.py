from pymongo import MongoClient
from datetime import datetime, timezone

def save_interface_status(ip, hostname, interfaces, routes):
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    collection = db["router_info"]

    router_doc = {
        "hostname": hostname,
        "ip_address": ip,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "status": "up",
        "interfaces": interfaces,
        "routes": routes
    }

    collection.insert_one(router_doc)

    client.close()

def save_config():
    pass