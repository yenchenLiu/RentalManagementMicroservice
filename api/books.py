import json
from io import BytesIO

import connexion
import opentracing
from fastavro import parse_schema, reader, writer
from flask_jwt_extended import get_jwt_identity, jwt_required
import settings

book_schema = parse_schema(json.loads(open("avro/Book.avsc", "r").read()))
category_schema = parse_schema(json.loads(open("avro/BookCategory.avsc", "r").read()))


def search():
    flask_tracer = settings.flask_tracer
    tracer = flask_tracer._tracer
    span = flask_tracer.get_span()
    
    with tracer.start_span("book_service:get_books", child_of=span) as sub_span:
        rpc = settings.rpc
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
    rpc = settings.rpc
    records = [data]
    with BytesIO() as f:
        writer(f, book_schema, records)
        f.seek(0)
        t = f.read().hex()
    connection = rpc.get_connection()
    result = connection.book_service.create_book(t)
    rpc.release_connection(connection)
        
    
    return result, 201
