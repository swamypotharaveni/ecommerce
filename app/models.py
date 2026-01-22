from sqlalchemy import Column,String,Float,Integer,BOOLEAN,DateTime
from.database import Base
from sqlalchemy.sql import func

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_active=Column(BOOLEAN,default=True,nullable=False)
    image_url=Column(String,nullable=True)
    stock_quantity=Column(Integer,default=0,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
