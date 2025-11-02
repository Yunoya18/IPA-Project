from pymongo import MongoClient

def get_router_info():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["netconfig_db"]
    routers = db["routers"]

    router_data = routers.find()
    return router_data
