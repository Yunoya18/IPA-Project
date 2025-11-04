from pymongo import MongoClient
import os

def get_router_info():
    mongo_uri  = os.environ.get("MONGO_URI")
    db_name    = os.environ.get("DB_NAME")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["routers"]

    router_data = list(routers.find())
    return router_data

def get_router_update():
    mongo_uri  = os.environ.get("MONGO_URI")
    db_name    = os.environ.get("DB_NAME")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["updates"]

    router_data = list(routers.find({"success" : "false"}))
    if not router_data:
        return []
    router_ids = [router["_id"] for router in router_data]
    routers.update_many({"_id": {"$in": router_ids}}, {"$set": {"success": "pending"}})
    return router_data