from __future__ import absolute_import

import opentracing
from django.apps import AppConfig
from django.conf import settings
from django_opentracing import DjangoTracer, OpenTracingMiddleware
from opentracing_instrumentation.request_context import RequestContextManager

from intracing.base import InspectorioTracerMixin, TracingHelper


class IntracingAppConfig(AppConfig):
    name = 'intracing'
    verbose_name = 'Inspectorio Tracing helper'

    def ready(self):
        IntracingDjangoMiddleware.configure_tracing()


class InspectorioDjangoTracer(InspectorioTracerMixin, DjangoTracer):

    def __init__(self, tracer_getter):
        self.__tracer = None
        self.__tracer_getter = tracer_getter
        self._current_spans = {}
        self._trace_all = True

    @property
    def _tracer(self):
        if not self.__tracer:
            self.__tracer = self.__tracer_getter()
        return self.__tracer


class IntracingDjangoMiddleware(OpenTracingMiddleware, TracingHelper):

    COMPONENT = 'Django'

    @classmethod
    def get_tracer(cls):
        return InspectorioDjangoTracer(cls.init_jaeger_tracer)

    @classmethod
    def configure_component(cls):
        cls.apply_patches()
        middleware_path = 'intracing.' + cls.__name__
        if settings.MIDDLEWARE is None:
            settings.MIDDLEWARE = []
        if middleware_path not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(0, middleware_path)

    def __init__(self, get_response):
        self.get_response = get_response
        self._tracer = opentracing.tracer

    def process_view(self, request, view_func, view_args, view_kwargs):
        super(IntracingDjangoMiddleware, self).process_view(
            request, view_func, view_args, view_kwargs
        )
        span = opentracing.tracer.get_span(request)
        self.set_request_tags(
            span, request.method, request.get_raw_uri()
        )
        request.tracing_context = RequestContextManager(span)
        request.tracing_context.__enter__()

    def process_response(self, request, response):
        span = opentracing.tracer.get_span(request)
        if span is None:
            return response

        self.set_response_tags(span, response.status_code)
        response = super(IntracingDjangoMiddleware, self).process_response(
            request, response
        )
        request.tracing_context.__exit__()
        return response
