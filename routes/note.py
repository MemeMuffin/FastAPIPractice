from typing import Union, Annotated
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.note import Note
from config.db import conn
from schemas.note import note_entity, notes_entity

note = APIRouter()
note.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@note.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Shows data recieved from database"""
    docs = conn.notes.notes.find({})
    new_docs = {}
    new_docs = notes_entity(docs)
    print(new_docs)
    # for doc in docs:
    #     new_docs.append(
    #         {
    #             "id": doc.get("_id"),
    #             "title": doc.get("title"),
    #             "description": doc.get("description"),
    #             "important": doc.get("important"),
    #         }
    #     )
    return templates.TemplateResponse("index.html", {"request": request, "new_docs": new_docs})


@note.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    """Example of Path parameter"""
    return ({"item_id": item_id, "q": q},)


@note.post("/")
async def add_note(request: Request):
    """Creates a note item in the database"""
    form = await request.form()
    data_to_store = dict(form)
    print(data_to_store)
    data_to_store["important"] = True if data_to_store.get("important") == "on" else False
    note = conn.notes.notes.insert_one(data_to_store)
    return {"Success": True}
