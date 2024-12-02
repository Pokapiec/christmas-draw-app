import random

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tinydb import TinyDB, Query


db = TinyDB("db/db.json")

Present = Query()
Presents = db.table("presents")

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates/css"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/generation", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "details.html", {})


@app.post("/presents")
async def presents_create(request: Request):
    data = await request.form()
    presents = data.getlist("present")
    person = data.get("person")
    if Presents.get(Present.person == person):
        Presents.update({"presents": presents}, Present.person == person)
    else:
        Presents.insert({"person": person, "presents": presents})

    return RedirectResponse("/", status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.get("/shuffle")
def get_shuffle():
    if results := db.all():
        return results[0]
    return {}


@app.get("/presents")
def get_presents():
    return Presents.all()


@app.post("/shuffle")
async def shuffle(request: Request):
    data = await request.form()
    names = data.getlist("name")
    bag = [*names]

    drawn_per_name = {}
    for name in names:
        others = [n for n in bag if n != name]
        drawn = random.choice(others)
        bag.remove(drawn)
        drawn_per_name[name] = drawn

    db.truncate()
    db.insert(drawn_per_name)
    return RedirectResponse(
        "/generation", status_code=status.HTTP_301_MOVED_PERMANENTLY
    )
