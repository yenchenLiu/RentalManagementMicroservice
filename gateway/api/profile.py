import json

import connexion
import opentracing
from flask_jwt_extended import get_jwt_identity, jwt_required
import settings


@jwt_required
def search():
    flask_tracer = settings.flask_tracer
    tracer = flask_tracer._tracer
    span = flask_tracer.get_span()
    
    with tracer.start_span("profile_service:get_profile", child_of=span) as sub_span:
        rpc = settings.rpc
        connection = rpc.get_connection()
        profile_id = get_jwt_identity()
        try:
            result = json.loads(connection.profile_service.get_profiles(profile_id))
        finally:
            rpc.release_connection(connection)
        sub_span.tags.append("finish")
        
    return result
