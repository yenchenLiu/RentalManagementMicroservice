import os

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nameko.rpc import rpc

import ipfsapi

Base = declarative_base()

class ItemImages(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, index=True, unique=True)
    item_hex = Column(String(100))

engine = create_engine('sqlite:///sqlite/file.db', echo=False)
Base.metadata.create_all(engine)

class FileService:
    name = "file_service"

    @rpc
    def insert_item_image(self, item_id, image):
        data = bytes.fromhex(image)
        with open('image_{}.png'.format(item_id), 'wb') as f:
            f.write(data)
        api = ipfsapi.connect(os.getenv("IPFS_HOST",'127.0.0.1'), 5001)
        res = api.add('image_{}.png'.format(item_id))

        Session = sessionmaker(bind=engine)
        session = Session()
        image = session.query(ItemImages).filter(ItemImages.item_id==item_id).one_or_none()
        if image is None:
            image = ItemImages(item_id=item_id, item_hex=res["Hash"])
            session.add(image)
        else:
            image.item_hex=res["Hash"]
        session.commit()

        result = {"url": "https://ipfs.io/ipfs/{}".format(res["Hash"])}
        return result

    @rpc
    def get_item_image(self, item_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        image = session.query(ItemImages).filter(ItemImages.item_id==item_id).one_or_none()
        if image is None:
            return {"error": "no image"}
        result = {"url": "https://ipfs.io/ipfs/{}".format(image.item_hex)}
        return result
    