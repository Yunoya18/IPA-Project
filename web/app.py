from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["netconfig_db"]
routers_collection = db["routers"]

title = "NetConfig - "

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    routers = list(routers_collection.find())
    return templates.TemplateResponse("index.html", {"title": title + "Home", "request" : request, "routers_list": routers})

@app.get("/detail")
async def router_detail(request: Request):
    return templates.TemplateResponse("router_detail.html", {"title": title + "Detail", "request" : request})

@app.post("/add")
async def add_router(
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
