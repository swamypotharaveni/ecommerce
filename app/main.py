from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from .database import Base,engine,SessionLocal
from.router.item_routes import router as item_routers
from fastapi.exceptions import RequestValidationError
from.models import ItemDB
from pathlib import Path
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)
app = FastAPI(title="My First FastAPI Project")
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images/"

app.mount("/images/", StaticFiles(directory=IMAGE_DIR), name="images")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": err["loc"][-1],
            "message": err["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={"success": False, "errors": errors}
    )
db = SessionLocal()

# # Set default values for old rows
# db.query(ItemDB).filter(ItemDB.is_active == None).update({ItemDB.is_active: True})
# db.query(ItemDB).filter(ItemDB.stock_quantity == None).update({ItemDB.stock_quantity: 0})
# db.commit()

app.include_router(item_routers)



