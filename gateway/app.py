import os

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
    app.add_api('rental.yaml', resolver=RestyResolver('api'), validate_responses=True, options={"swagger_ui": True}) # require connexion[swagger-ui]
    application = app.app
    settings.init(application)

    SECRET_KEY = os.environ["JWT_SECRET"]
    application.config['SECRET_KEY'] = SECRET_KEY
    jwt = JWTManager(application)
    app.run()
