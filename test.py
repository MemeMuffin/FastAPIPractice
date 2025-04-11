# from typing import Union

from typing import Annotated, Literal
from datetime import datetime
import random
from fastapi import (
    FastAPI,
    Request,
    Query,
    Path,
    Body,
    Cookie,
    Header,
    status,
    Form,
    File,
    UploadFile,
    HTTPException,
    Depends,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, AfterValidator, Field
from pymongo import MongoClient

conn = MongoClient("mongodb+srv://mutayyabh02:hafeez12@cluster0.s9ye04b.mongodb.net/notes")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    docs = conn.notes.notes.find({})
    new_docs = []
    for doc in docs:
        new_docs.append({"id": doc["_id"], "note": doc["note"]})
    return templates.TemplateResponse("index.html", {"request": request, "new_docs": new_docs})


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    """Example of Path parameter"""
    return {"item_id": item_id, "q": q}


@app.get("/users/me")
async def read_user_me():
    """General get request"""
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """General get request with path parameter"""
    return {"user_id": user_id}


@app.get("/users")
async def read_users():
    """List get method"""
    return ["Rick", "Morty"]


@app.get("/users")
async def read_users2():
    """List get method"""
    return ["Bean", "Elfo"]


class Item(BaseModel):
    """General body for parameter usage"""

    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    """General get request using body"""
    return item


@app.get("/items1/")
async def read_items1(q: Annotated[list[str] | None, Query()] = None):
    """General Annotated parameter example"""
    query_items = {"q": q}
    return query_items


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    """Checks for custom valid id after system validation"""
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items2/")
async def read_items2(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    """General usage of custom validator in validation"""
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}


class FilterParams(BaseModel):
    """General body"""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items3/")
async def read_items3(filter_query: Annotated[FilterParams, Query()]):
    """General multi-body query"""
    return filter_query


@app.get("/items4/")
async def read_items4(ads_id: Annotated[str | None, Cookie()] = None):
    """General request to see cookie parameter in use"""
    return {"ads_id": ads_id}


@app.get("/items5/")
async def read_items5(user_agent: Annotated[str | None, Header()] = None):
    """General request to see header parameter in use"""
    return {"User-Agent": user_agent}


items = {"foo": "The Foo Wrestlers"}


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    """Throws HTTPException when item is not found in data"""
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


fake_db = {}


class Item1(BaseModel):
    """Simple item model"""

    title: str
    timestamp: datetime
    description: str | None = None


@app.put("/items/{id}")
def update_item(id: str, item: Item1):
    """Converts pydantic model into jsonable data"""
    json_compatible_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_data


class Item2(BaseModel):
    """General Item model"""

    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items1/{item_id}", response_model=Item2)
async def read_item6(item_id: str):
    """Shows stored data in Item model"""
    return items[item_id]


@app.patch("/items/{item_id}", response_model=Item2)
async def update_item1(item_id: str, item: Item2):
    """Updates data in model Item's value"""
    stored_item_data = items[item_id]
    stored_item_model = Item2(**stored_item_data)
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    """General class with some attributes"""

    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    """General function which has some dependencies"""
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
