from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
import uvicorn

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "netconfig_db"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

title = "NetConfig - "

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Device(BaseModel):
    ip_address: str
    username: str
    password: str

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"title": title + "Home", "request" : request})

@app.post("/api/devices")
def save_device(device: Device):
    try:
        result = db.devices.insert_one(device.dict())
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
