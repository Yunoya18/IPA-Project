from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
import uvicorn
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["netconfig_db"]
routers_collection = db["routers"]
router_info_collection = db["router_info"]

title = "NetConfig - "

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    routers = list(routers_collection.find())
    return templates.TemplateResponse("index.html", {"title": title + "Home", "request" : request, "routers_list": routers})

@app.get("/detail/{router_id}", response_class=HTMLResponse)
def router_detail(request: Request, router_id: str):
    try:
        obj_id = ObjectId(router_id)

        router_auth = routers_collection.find_one({"_id": obj_id})
        if router_auth is None:
            raise HTTPException(status_code=404, detail="Router auth data not found")

        ip_to_find = router_auth.get("ip_address")
        router_data = router_info_collection.find_one({"ip_address": ip_to_find})

        return templates.TemplateResponse("router_detail.html", {
            "title": title + "Detail - " + ip_to_find, 
            "request" : request,
            "router_auth": router_auth, # ข้อมูลจาก collection 'routers'
            "router_info": router_data  # ข้อมูลจาก collection 'router_info'
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
def add_router(
    ip_address: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        router = {
            "ip_address": ip_address,
            "username": username,
            "password": password,
        }
        routers_collection.insert_one(router)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
