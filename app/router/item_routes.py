from fastapi import FastAPI,HTTPException,APIRouter,Query,Depends,File,Form,UploadFile
from sqlalchemy.orm import session
from typing import Optional
from sqlalchemy import asc, desc,or_
from pathlib import Path
from..schemas import ItemCreate,Item,PaginatedItems,BulkDeleteItems
from..dependencies import get_db
from..models import ItemDB
import uuid
import shutil
import os
from fastapi.requests import Request
router=APIRouter()
IMAGE_DIR = Path("app/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

async def Save_Image(image:UploadFile,request:Request):
    if image is None:
        raise HTTPException(status_code=400,detail="image is not upload")
    content= await image.read()
    if len(content)> 2*1024*1024:
         raise HTTPException(status_code=400,detail=f"upload a images too large! {image.content_type}")
    if image.content_type not in ["image/png","image/jpeg"]:
        raise HTTPException(status_code=400,detail="this file is not accepted!")
    filename=f"{uuid.uuid4()}_{image.filename}"
    image.file.seek(0)
    file_path=IMAGE_DIR/filename
    with file_path.open('wb+') as buffer:
        shutil.copyfileobj(image.file,buffer)
        base_url = str(request.base_url) 
    return f"{base_url}images/{filename}"
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
async def creare_item(name:str=Form(...),
                      description:str=Form(None),
                       price:float=Form(...),
                       is_active:bool=Form(True),
                       stock_quantity:int=Form(0),
                       request:Request=None,
                       image:UploadFile=File(None),db:session=Depends(get_db)):
    image_url=await Save_Image(image,request) if image else None
    db_items=ItemDB(name=name,
        description=description,
        price=price,
        is_active=is_active,
        stock_quantity=stock_quantity,
        image_url=image_url)
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

@router.post('/items/bulk_delete')
def bulk_delete_items(payload:BulkDeleteItems,db:session=Depends(get_db)):
    items_to_delete = db.query(ItemDB).filter(ItemDB.id.in_(payload.item_ids)).all()
    print(items_to_delete)
    if not items_to_delete:
        raise HTTPException(status_code=404, detail="No items found for given IDs")
    deleted_ids=[]
    for item in items_to_delete:
        if item.image_url:
            print(item.image_url)
            filename = item.image_url.split("/")[-1]
            file_path = IMAGE_DIR / filename
            print(file_path)
            if file_path.exists():
                os.remove(file_path)
        deleted_ids.append(item.id)
        db.delete(item)
    db.commit()
    return {
        "deleted_count": len(deleted_ids),
        "deleted_ids":deleted_ids
    }



    