from sqlalchemy import Column,String,Float,Integer,BOOLEAN
from.database import Base

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_active=Column(BOOLEAN,default=True,nullable=False)