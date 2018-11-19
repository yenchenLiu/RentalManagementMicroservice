import os
import logging

import opentracing
from flask import _request_ctx_stack as stack
from jaeger_client import Config
from jaeger_client import Tracer


def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
             'local_agent': {
                'reporting_host': "{}".format(os.getenv("REPORTING_HOST", "localhost")),
            },
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()



class FlaskTracer(Tracer):
    '''
    Tracer that can trace certain requests to a Flask app.
    @param tracer the OpenTracing tracer implementation to trace requests with
    '''
    def __init__(self, tracer, trace_all_requests=False, app=None, traced_attributes=[]):
        if not callable(tracer):
            self.__tracer = tracer
        else:
            self.__tracer = None
            self.__tracer_getter = tracer
        self._trace_all_requests = trace_all_requests
        self._current_spans = {}

        # tracing all requests requires that app != None
        if self._trace_all_requests:
            @app.before_request
            def start_trace():
                self._before_request_fn(traced_attributes)

            @app.after_request
            def end_trace(response):
                self._after_request_fn()
                return response

    @property
    def _tracer(self):
        if not self.__tracer:
            self.__tracer = self.__tracer_getter()
        return self.__tracer

    def trace(self, *attributes):
        '''
        Function decorator that traces functions
        NOTE: Must be placed after the @app.route decorator
        @param attributes any number of flask.Request attributes
        (strings) to be set as tags on the created span
        '''
        def decorator(f):
            def wrapper(*args, **kwargs):
                if not self._trace_all_requests:
                    self._before_request_fn(list(attributes))
                    r = f(*args, **kwargs)
                    self._after_request_fn()
                    return r
                else:
                    return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        return decorator

    def get_span(self, request=None):
        '''
        Returns the span tracing `request`, or the current request if
        `request==None`.
        If there is no such span, get_span returns None.
        @param request the request to get the span from
        '''
        if request is None and stack.top:
            request = stack.top.request
        return self._current_spans.get(request, None)

    def _before_request_fn(self, attributes):
        request = stack.top.request
        operation_name = request.endpoint
        headers = {}
        for k,v in request.headers:
            headers[k.lower()] = v
        span = None
        try:
            span_ctx = self._tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
            span = self._tracer.start_span(operation_name=operation_name, child_of=span_ctx)
        except (opentracing.InvalidCarrierException, opentracing.SpanContextCorruptedException) as e:
            span = self._tracer.start_span(operation_name=operation_name, tags={"Extract failed": str(e)})
        if span is None:
            span = self._tracer.start_span(operation_name)
        self._current_spans[request] = span
        for attr in attributes:
            if hasattr(request, attr):
                payload = str(getattr(request, attr))
                if payload:
                    span.set_tag(attr, payload)

    def _after_request_fn(self):
        request = stack.top.request
        # the pop call can fail if the request is interrupted by a `before_request` method so we need a default
        span = self._current_spans.pop(request, None)
        if span is not None:
            span.finish()
