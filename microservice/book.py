import json
from io import BytesIO

from fastavro import parse_schema, reader, writer
from nameko.rpc import rpc
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

book_schema = parse_schema(json.loads(open("../avro/Book.avsc", "r").read()))
category_schema = parse_schema(json.loads(open("../avro/BookCategory.avsc", "r").read()))

Base = declarative_base()

class BookCategory(Base):
    __tablename__ = 'book_category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    book = relationship("Book", back_populates='category')

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('book_category.id'), nullable=True)
    category = relationship("BookCategory", back_populates="book")
    name = Column(String(50))
    amount = Column(Integer)

engine = create_engine('sqlite:///book.db', echo=False)
Base.metadata.create_all(engine)

class BookService:
    name = "book_service"

    @rpc
    def create_category(self, data):
        Session = sessionmaker(bind=engine)
        session = Session()
        with BytesIO() as f:
            f.write(bytes.fromhex(data))
            f.seek(0)
            avro_reader = reader(f, category_schema)
            for data in avro_reader:
                category = category(name=data["name"])
                session.add(category)
                session.commit()

        session.close()
        return "success"

    @rpc
    def create_book(self, data):
        Session = sessionmaker(bind=engine)
        session = Session()
        with BytesIO() as f:
            f.write(bytes.fromhex(data))
            f.seek(0)
            avro_reader = reader(f, book_schema)
            for data in avro_reader:
                category = None
                if data["category"]:
                    category = session.query(BookCategory).filter_by(id=data["category"]).first()
                book = Book(name=data["name"], amount=data["amount"])
                if category:
                    book.category = category
                session.add(book)
                session.commit()

        session.close()
        return "success"
    
    @rpc
    def get_books(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        records = []
        result = {}
        t = None
        for book in session.query(Book):
            records.append({"id": book.id, "name": book.name, "category": book.category_id, "amount":book.amount})
        with BytesIO() as f:
            writer(f, book_schema, records)
            f.seek(0)
            t = f.read().hex()
        result["book"] = t
        
        records = []
        t = None

        for category in session.query(BookCategory):
            records.append({"id": category.id, "name": category.name})
        with BytesIO() as f:
            writer(f, category_schema, records)
            f.seek(0)
            t = f.read().hex()
        result["category"] = t
        session.close()
        return json.dumps(result)
