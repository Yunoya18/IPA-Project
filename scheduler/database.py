from pymongo import MongoClient

def get_router_info():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    routers = db["routers"]

    router_data = routers.find()
    return router_data

def get_router_update():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    routers = db["updates"]

    router_data = routers.find({"success" : "false"})
    for router in router_data:
        routers.update_one({"_id": router["_id"]}, {"$set": {"success": "pending"}})
    return router_data
