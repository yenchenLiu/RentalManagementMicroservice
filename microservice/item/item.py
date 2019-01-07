import json
import os
from io import BytesIO

from nameko.rpc import rpc
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.exc import ProgrammingError

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

engine = create_engine('mysql+pymysql://root:testpassword@{}/item'.format(os.getenv("MYSQL_HOST", "localhost")), echo=False)
Base.metadata.create_all(engine)


class ItemService:
    name = "item_service"

    @rpc
    def insert_item(self, category_name, name):
        Session = sessionmaker(bind=engine)
        session = Session()
        category = session.query(ItemCategory).filter(ItemCategory.name==category_name).first()
        if category is None:
            category = ItemCategory(name=category_name)
            session.add(category)
            session.commit()
        item = session.query(Item).filter(Item.name==name, Item.category_id==category.id).one_or_none()
        if item is None:
            item = Item(name=name, category=category, amount=1)
            session.add(item)
        else:
            item.amount += 1
        session.commit()
        result = {"name": item.name, "id": item.id}
        session.close()
        return json.dumps(result)
    
    @rpc
    def rent_item(self, item_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        item = session.query(Item).get(item_id)
        if item.amount <= 0:
            return False
        item.amount -= 1
        session.commit()
        name = item.name
        session.close()
        return {"id":item_id, "name":name}

    @rpc
    def return_item(self, item_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        item = session.query(Item).get(item_id)
        item.amount += 1
        session.commit()
        name = item.name
        session.close()
        return {"id":item_id, "name":name}
    
    @rpc
    def check_item(self, item_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        item = session.query(Item).get(item_id)
        if item is None:
            return False
        if item.amount <= 0:
            return False
        session.close()
        return True

    @rpc
    def get_items(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        result = []
        for item in session.query(Item):
            result.append({"id": item.id, "amount": item.amount, 
            "category-id": item.category_id, "name": item.name})
        session.close()
        return json.dumps(result)

    # @rpc
    # def create_category(self, name):
    #     Session = sessionmaker(bind=engine)
    #     session = Session()
    #     if session.query(exists().where(ItemCategory.name==name)).scalar():
    #         return json.dumps({"error": "分類已經存在"})
    #     category = ItemCategory(name=name)
    #     session.add(category)
    #     session.commit()
    #     result = {"name": category.name, "id": category.id}
    #     session.close()
    #     return json.dumps(result)

    @rpc
    def get_category(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        result = []
        for category in session.query(ItemCategory):
            result.append({"id": category.id, "name": category.name})
        session.close()
        return json.dumps(result)
