from fastapi import FastAPI
from .database import Base,engine
from.router.item_routes import router as item_routers

Base.metadata.create_all(bind=engine)
app = FastAPI(title="My First FastAPI Project")

app.include_router(item_routers)


