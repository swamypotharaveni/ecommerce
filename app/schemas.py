from pydantic import BaseModel
from typing import List
class ItemCreate(BaseModel):
    name:str
    description:str|None=None
    price:float
class Item(ItemCreate):
    id:int

class PaginatedItems(BaseModel):
    total_count:int
    items:List[Item]