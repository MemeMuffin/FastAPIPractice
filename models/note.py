from typing import Union
from pydantic import BaseModel


class Note(BaseModel):
    """Model for Notes"""

    title: str
    description: Union[str, None] = None
    important: Union[bool, None] = None
