import json
from io import BytesIO

from fastavro import parse_schema, reader, writer
from fastavro.validation import validate

from . import rpc
from flask_jwt_extended import get_jwt_identity, jwt_required

book_schema = parse_schema(json.loads(open("avro/Book.avsc", "r").read()))
category_schema = parse_schema(json.loads(open("avro/BookCategory.avsc", "r").read()))

def search():
    print(get_jwt_identity())
    connection = rpc.get_connection()
    result = json.loads(connection.book_service.get_books())
    rpc.release_connection(connection)

    category = {}
    with BytesIO() as f:
        f.write(bytes.fromhex(result["category"]))
        f.seek(0)
        avro_reader = reader(f, category_schema)
        for data in avro_reader:
            category[data["id"]] = data["name"]

    books = []
    with BytesIO() as f:
        f.write(bytes.fromhex(result["book"]))
        f.seek(0)
        avro_reader = reader(f, book_schema)
        for data in avro_reader:
            if data["category"] in category:
                books.append({"id": data["id"], "name": data["name"], "category": category[data["category"]], "amount": data["amount"]})
            else:
                books.append({"id": data["id"], "name": data["name"], "category": "未分類", "amount": data["amount"]})
    
    return books

@jwt_required
def post(data):
    records = [data]
    with BytesIO() as f:
        writer(f, book_schema, records)
        f.seek(0)
        t = f.read().hex()
    connection = rpc.get_connection()
    result = connection.book_service.create_book(t)
    rpc.release_connection(connection)
        
    
    return result, 201
