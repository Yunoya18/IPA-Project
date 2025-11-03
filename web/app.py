from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
from pymongo import MongoClient
import uvicorn

# --- MongoDB ---
client = MongoClient("mongodb://mongo:27017/")
db = client["netconfig_db"]
routers_collection = db["routers"]
router_info_collection = db["router_info"]
update_collection = db["updates"]

# --- App / Templating ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
TITLE = "NetConfig - "

@app.get("/")
def home(request: Request):
    routers = list(routers_collection.find())
    return templates.TemplateResponse(
        "index.html",
        {"title": TITLE + "Home", "request": request, "routers_list": routers},
    )

@app.get("/detail/{router_id}", response_class=HTMLResponse)
def router_detail(request: Request, router_id: str):
    obj_id = ObjectId(router_id)
    router_auth = routers_collection.find_one({"_id": obj_id})
    if not router_auth:
        raise HTTPException(status_code=404, detail="Router auth data not found")

    ip_to_find = router_auth.get("ip_address")
    router_data = router_info_collection.find_one({"ip_address": ip_to_find})

    return templates.TemplateResponse(
        "router_detail.html",
        {
            "title": TITLE + f"Detail - {ip_to_find}",
            "request": request,
            "router_auth": router_auth,
            "router_info": router_data,
        },
    )

@app.post("/add")
def add_router(
    ip_address: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    routers_collection.insert_one(
        {"ip_address": ip_address, "username": username, "password": password}
    )
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{router_id}")
def delete_router(router_id: str):
    obj_id = ObjectId(router_id)
    result = routers_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Router not found")
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/update")
async def api_update(request: Request):
    data = await request.json()

    ip_router = (data.get("ip_router") or "").strip()
    iface = data.get("interface") or {}
    name = (iface.get("name") or "").strip()
    ip_address = (iface.get("ip_address") or "").strip()
    subnet_mask = (iface.get("subnet_mask") or "").strip()
    status = (iface.get("status") or "up").strip().lower()

    missing = []
    if not ip_router:   missing.append("ip_router")
    if not name:        missing.append("interface.name")
    if not ip_address:  missing.append("interface.ip_address")
    if not subnet_mask: missing.append("interface.subnet_mask")
    if status not in ("up", "down"):
        raise HTTPException(status_code=400, detail="status must be 'up' or 'down'")
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Missing required fields: {', '.join(missing)}"
        )


    r1 = update_collection.update_one(
        {"ip_router": ip_router, "interfaces.name": name},
        {"$set": {
            "interfaces.$.ip_address": ip_address,
            "interfaces.$.subnet_mask": subnet_mask,
            "interfaces.$.status": status,
            "interfaces.$.success": False,
        }},
    )

    if r1.matched_count == 0:
        update_collection.update_one(
            {"ip_router": ip_router},
            {
                "$setOnInsert": {"ip_router": ip_router},
                "$push": {
                    "interfaces": {
                        "name": name,
                        "ip_address": ip_address,
                        "subnet_mask": subnet_mask,
                        "status": status,
                        "success": False,
                    }
                },
            },
            upsert=True,
        )

    return {"ok": True}

@app.get("/api/update/status")
def api_update_status(ip_router: str, name: str):
    doc = update_collection.find_one(
        {"ip_router": ip_router, "interfaces.name": name},
        {"_id": 0, "interfaces.$": 1},
    )
    if not doc or "interfaces" not in doc or not doc["interfaces"]:
        return {"success": False}
    return {"success": bool(doc["interfaces"][0].get("success", False))}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
