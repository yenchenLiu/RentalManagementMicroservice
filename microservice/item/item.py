import json
from io import BytesIO

from nameko.rpc import rpc
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import exists

Base = declarative_base()


class ItemCategory(Base):
    __tablename__ = 'item_category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    item = relationship("Item", back_populates='category')

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('item_category.id'), nullable=True)
    category = relationship("ItemCategory", back_populates="item")
    name = Column(String(50))
    amount = Column(Integer)

engine = create_engine('sqlite:///item.db', echo=False)
Base.metadata.create_all(engine)

class ItemService:
    name = "item_service"

    @rpc
    def create_category(self, name):
        Session = sessionmaker(bind=engine)
        session = Session()
        if session.query(exists().where(ItemCategory.name==name)).scalar():
            return json.dumps({"error": "分類已經存在"})
        category = ItemCategory(name=name)
        session.add(category)
        session.commit()
        category_id = category.id
        session.close()
        result = {"name": category.name, "id": category.id}
        return json.dumps(result)
    
    @rpc
    def get_category(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        result = []
        for category in session.query(ItemCategory):
            result.append({"id": category.id, "name": category.name})
        session.close()
        return json.dumps(result)
