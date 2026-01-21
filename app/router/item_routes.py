from fastapi import FastAPI,HTTPException,APIRouter,Query,Depends
from sqlalchemy.orm import session
from typing import Optional
from sqlalchemy import asc, desc,or_

from..schemas import ItemCreate,Item,PaginatedItems
from..dependencies import get_db
from..models import ItemDB
router=APIRouter()
@router.get('/items/',response_model=PaginatedItems)
async def items(db:session=Depends(get_db),
                skip:int=Query(0,ge=0),
                limit:int=Query(10,ge=1,le=100),
                name:Optional[str]=Query(None),
                q:Optional[str]=Query(None),
                status:Optional[str]=Query("all"),
                price_min:Optional[float]=Query(None,ge=0),price_max:Optional[float]=Query(None,ge=0)):
    # query = db.query(ItemDB)
    # if status == "all":
    #     query = db.query(ItemDB)
    # else:
    #      query = db.query(ItemDB).filter(ItemDB.is_active==status)
    query = db.query(ItemDB)
    if status.lower() == "active":
        query = query.filter(ItemDB.is_active == True)
    elif status.lower() == "inactive":
        query = query.filter(ItemDB.is_active == False)

    if q is not None:
        query=query.filter(
            or_(ItemDB.name.like(f"%{q}%"),ItemDB.price.like(f"%{q}%"))
        )
    if name:
        query=query.filter(ItemDB.name.like(f"%{name}%"))
    if price_min is not None:
        query=query.filter(ItemDB.price >=price_min)
    if price_max is not None:
        query=query.filter(ItemDB.price<=price_max)

    total_count=query.count()
    paginated_items=query.order_by(ItemDB.id.desc()).offset(skip).limit(limit).all()
  
    

    return {
        "total_count":total_count,
        "items":paginated_items

    }

@router.post('/items/',response_model=Item)
async def creare_item(item:ItemCreate,db:session=Depends(get_db)):
    db_items=ItemDB(**item.model_dump())
    db.add(db_items)
    db.commit()
    db.refresh(db_items)
    return db_items

@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int,db:session=Depends(get_db)):
    item_db=db.query(ItemDB).filter(ItemDB.id==item_id).first()
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_db
    
@router.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate,db:session=Depends(get_db)):
    item_db=db.query(ItemDB).filter(ItemDB.id==item_id).first()
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    for key,valu in item.model_dump().items():
        setattr(item_db,key,valu)
    
    db.commit()
    db.refresh(item_db)
    return item_db
@router.delete("/items/{item_id}")
def delete_items(item_id: int,db:session=Depends(get_db)):
    db_item=db.query(ItemDB).filter(ItemDB.id==item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

    