import json

import connexion
import opentracing
from flask_jwt_extended import get_jwt_identity, jwt_required
import settings


def search():
    rpc = settings.rpc
    connection = rpc.get_connection()
    try:
        result = json.loads(connection.profile_service.get_profiles(1))
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