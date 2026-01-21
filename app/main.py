from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from .database import Base,engine
from.router.item_routes import router as item_routers
from fastapi.exceptions import RequestValidationError

Base.metadata.create_all(bind=engine)
app = FastAPI(title="My First FastAPI Project")
print("ks")

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

app.include_router(item_routers)



