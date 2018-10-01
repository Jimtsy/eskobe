# -*- coding:utf-8 -*-

from utils import camel_case_to_lower_case, make_sequence_key
from response import NotFound, ServerErr
from log import logger
from functools import wraps


def _cached_func_object(func):
    cached = {}

    @wraps(func)
    def wrap(*args, **kwargs):
        k = make_sequence_key(*args, **kwargs)
        if k not in cached:
            cached[k] = func(*args, **kwargs)
        return cached[k]
    return wrap


@_cached_func_object
def _get_func_object(cls_object_list, func_name):
    for obj_cls in cls_object_list:
        if hasattr(obj_cls, func_name):
            return getattr(obj_cls, func_name)
    return None


def request_middleware(request,  **kwargs):
    app = kwargs.get('app', None)
    func = kwargs.get('function', None)

    if not all([app, func]):
        return NotFound()

    func = camel_case_to_lower_case(func)

    try:
        obj_app = __import__("%s.views" % app)
    except ImportError:
        return ServerErr("Import error, not founded {}.views".format(app))

    obj_view = getattr(obj_app, 'views')

    if not hasattr(obj_view, "__all__"):
        return ServerErr("Undefined {}.__all__".format(obj_view))

    obj_cls_list = [getattr(obj_view, cls) for cls in obj_view.__all__ if hasattr(obj_view, cls)]
    obj_func = _get_func_object(obj_cls_list, func)
    if obj_func:
        return obj_func(request)
    else:
        return NotFound()