from lib.tracing import FlaskTracer, init_tracer
from flask import Flask
from flask_nameko import FlaskPooledClusterRpcProxy


def init(application):
    global flask_tracer
    global rpc
    flask_tracer = FlaskTracer(init_tracer("book store"), True, application)
    rpc = FlaskPooledClusterRpcProxy()

    def create_app():
        rpc_app = Flask(__name__)
        rpc_app.config.update(dict(
            NAMEKO_AMQP_URI='pyamqp://guest:guest@localhost:5674/;pyamqp://guest:guest@localhost:5673/;pyamqp://guest:guest@localhost:5672/'
        ))

        rpc.init_app(rpc_app)
    create_app()