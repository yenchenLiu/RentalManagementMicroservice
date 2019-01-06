import os
import json

from nameko.rpc import rpc
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Profile(Base):
    __tablename__ = 'profile'
    
    id = Column(Integer, primary_key=True)
    point = Column(Integer)
    lends = relationship("Lends", back_populates='profile')

class Lends(Base):
    __tablename__ = 'lends'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=True)
    profile = relationship("Profile", back_populates="lends")
    item_id = Column(Integer)
    name = Column(String(50))
    returned = Column(Boolean)

engine = create_engine('mysql+pymysql://root:testpassword@{}/profile'.format(os.getenv("MYSQL_HOST", "localhost")), echo=False)
Base.metadata.create_all(engine)

class ProfileService:
    name = "profile_service"

    @rpc
    def get_profiles(self, profile_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        lends = []
        returns = []
        result = {}

        profile = session.query(Profile).get(profile_id)
        
        # 建立新使用者
        if profile is None:
            profile = Profile(id=profile_id ,point=10)
            session.add(profile)
            session.commit()

        for lend in session.query(Lends).filter(profile_id==profile_id):
            lends.append({"id":lend.id, "name": lend.name, "return": lend.returned})
        
        result["point"] = profile.point
        result["lends"] = lends
        
        session.close()
        return json.dumps(result)
    
    @rpc
    def check_point(self, profile_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        profile = session.query(Profile).get(profile_id)
        # 建立新使用者
        if profile is None:
            profile = Profile(id=profile_id ,point=10)
            session.add(profile)
            session.commit()
        point = profile.point
        session.close()
        return point

    @rpc
    def rent_item(self, profile_id ,item_id, name):
        Session = sessionmaker(bind=engine)
        session = Session()
        profile = session.query(Profile).get(profile_id)
        # 建立新使用者
        if profile is None:
            profile = Profile(id=profile_id ,point=10)
            session.add(profile)
            session.commit()
        if profile.point <= 0:
            return False
        lend = Lends(profile=profile, item_id=item_id, name=name, returned=False)
        session.add(lend)
        profile.point -= 1
        session.commit()
        point = profile.point
        session.close()
        return point
    
    @rpc
    def return_item(self, profile_id ,lend_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        profile = session.query(Profile).get(profile_id)
        # 建立新使用者
        if profile is None:
            profile = Profile(id=profile_id ,point=10)
            session.add(profile)
            session.commit()
            return False
        lend = session.query(Lends).get(lend_id)
        if lend is None or lend.returned is True:
            return False
        
        lend.returned = True
        item_id = lend.item_id
        session.commit()
        return item_id