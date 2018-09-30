# -*- coding: utf-8 -*-

from django.conf.urls import url
from .middle import request_middleware


urlpatterns = [
    url('^(?P<app>(\w+))/(?P<function>(\w+))/$', request_middleware),
    url('^(?P<app>(\w+))/(?P<function>(\w+))', request_middleware),
    url('^(?P<function>(\w+))/$', request_middleware),
    url('^(?P<function>(\w+))', request_middleware)
]