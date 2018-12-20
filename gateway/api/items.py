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

def create_category(data):
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = json.loads(connection.item_service.create_category(data["name"]))
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
    if "error" in result:
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
    if "error" in result:
        return result, 400
    return result
