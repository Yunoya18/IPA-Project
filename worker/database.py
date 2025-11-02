from pymongo import MongoClient
from datetime import datetime, UTC

def save_interface_status(router_ip, interfaces):

    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    collection = db["router_info"]

    data = {
        "router_ip": router_ip,
        "timestamp": datetime.now(UTC),
        "interfaces": interfaces,
    }
    collection.insert_one(data)
    client.close()
