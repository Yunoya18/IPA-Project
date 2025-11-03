from pymongo import MongoClient

def get_router_info():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    routers = db["routers"]

    router_data = list(routers.find())
    return router_data

def get_router_update():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    routers = db["updates"]

    router_data = list(routers.find({"success" : "false"}))
    if not router_data:
        return []
    router_ids = [router["_id"] for router in router_data]
    routers.update_many({"_id": {"$in": router_ids}}, {"$set": {"success": "pending"}})
    return router_data
