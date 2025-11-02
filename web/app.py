from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

title = "NetConfig - "

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"title": title + "Home", "request" : request})

@app.get("/detail")
async def router_detail(request: Request):
    return templates.TemplateResponse("router_detail.html", {"title": title + "Detail", "request" : request})

@app.get("/add")
async def add_router(requset: Request):
    pass

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
