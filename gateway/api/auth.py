import hashlib
from flask_jwt_extended import create_access_token
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import exists

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))


engine = create_engine('sqlite:///auth.db', echo=False)
Base.metadata.create_all(engine)

def post(data):
    Session = sessionmaker(bind=engine)
    session = Session()
    m = hashlib.sha256()
    m.update(data["username"].encode())
    m.update(data["password"].encode())
    password = m.hexdigest()
    user = session.query(User).filter(User.username==data["username"]).filter(User.password==password).one_or_none()

    if user is None:
        return {"msg": "Bad username or password"}, 401
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user.id)
    return {"access_token": access_token}, 200

def create_user(data):
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(exists().where(User.username==data["username"])).scalar():
        return "帳號已經註冊過", 400
    
    m = hashlib.sha256()
    m.update(data["username"].encode())
    m.update(data["password"].encode())
    password = m.hexdigest()
    user = User(username=data["username"], password=password)
    session.add(user)
    session.commit()
    return "OK", 201