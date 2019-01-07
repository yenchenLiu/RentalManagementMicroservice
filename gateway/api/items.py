import json

import connexion
import opentracing
from flask_jwt_extended import get_jwt_identity, jwt_required
import settings


def search():
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = json.loads(connection.item_service.get_items())
    finally:
        rpc.release_connection(connection)
    return result

def get_category():
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = json.loads(connection.item_service.get_category())
    finally:
        rpc.release_connection(connection)
    if "error" in result:
        return result, 400
    return result


def create_item(image, categoryname, name):
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = json.loads(connection.item_service.insert_item(categoryname, name))
        if image:
            print(type(image))
            connection.file_service.insert_item_image(result["id"], image.read().hex())
    finally:
        rpc.release_connection(connection)
    if "error" in result:
        return result, 400

    return result

def get_item_image(item_id):
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = connection.file_service.get_item_image(item_id)
    finally:
        rpc.release_connection(connection)
    if "error" in result:
        return result, 400

    return result

@jwt_required
def rent(data):
    profile_id = get_jwt_identity()
    item_id = data["item_id"]
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = connection.rent_service.rent_item(profile_id, item_id)
    finally:
        rpc.release_connection(connection)
    if "error" in result and result["error"] is True:
        return result, 400
    return result

@jwt_required
def returned(data):
    profile_id = get_jwt_identity()
    lend_id = data["lend_id"]
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = connection.rent_service.return_item(profile_id, lend_id)
    finally:
        rpc.release_connection(connection)
    if "error" in result and result["error"] is True:
        return result, 400
    return result
