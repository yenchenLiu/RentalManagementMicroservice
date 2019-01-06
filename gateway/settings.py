import os
from lib.tracing import FlaskTracer, init_tracer
from flask import Flask
from flask_nameko import FlaskPooledClusterRpcProxy


def init(application):
    global flask_tracer
    global rpc
    flask_tracer = FlaskTracer(init_tracer("item rental"), True, application)
    rpc = FlaskPooledClusterRpcProxy()

    def create_app():
        rpc_app = Flask(__name__)
        rpc_app.config.update(dict(
            NAMEKO_AMQP_URI='pyamqp://{}:{}@{}'.format(os.getenv('RABBITMQ_USER', "guest"), os.getenv('RABBITMQ_PASSWORD', "guest"), 
                                                       os.getenv('RABBITMQ_HOST', "localhost"))
        ))

        rpc.init_app(rpc_app)
    create_app()

def rpc_reconnect():
    global rpc
    print(rpc.get_connection)