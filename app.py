from random import randint

import connexion
import opentracing
from connexion.resolver import RestyResolver

from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)
from lib.tracing import init_tracer

import settings

if __name__ == "__main__":
    app = connexion.App(__name__, port=9090, specification_dir='swagger/')
    app.add_api('shopping.yaml', resolver=RestyResolver('api'),
                swagger_ui=True, validate_responses=True)
    application = app.app
    settings.init(application)

    SECRET_KEY = ""
    for _ in range(50):
        SECRET_KEY += chr(randint(32,126))
    application.config['SECRET_KEY'] = SECRET_KEY
    jwt = JWTManager(application)
    app.run()
