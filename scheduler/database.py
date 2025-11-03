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

    router_data = routers.find({"success" : False})
    return router_data