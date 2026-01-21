from pydantic import BaseModel,field_validator
from typing import List
class ItemCreate(BaseModel):
    name:str
    description:str|None=None
    price:float
    is_active:bool=True
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty!")
        return v

    @field_validator("price")
    @classmethod
    def price_valid(cls, v):
        if v < 0:
            raise ValueError("Price must be greater than or equal to 0")
        return v
class Item(ItemCreate):
    id:int

    class config:
        from_attributes = True

class PaginatedItems(BaseModel):
    total_count:int
    items:List[Item]