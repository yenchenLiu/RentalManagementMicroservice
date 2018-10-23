from flask_jwt_extended import create_access_token



def post(data):
    if data["username"] != 'test' or data["password"] != 'test':
        return {"msg": "Bad username or password"}, 401
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=data["username"])
    return {"access_token": access_token}, 200
