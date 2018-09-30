# -*- coding:utf-8 -*-

from utils import camel_case_to_lower_case
from response import NotFound, ServerErr
from log import logger


def request_middleware(request,  **kwargs):
    app = kwargs.get('app', None)
    func = kwargs.get('function', None)
    func = camel_case_to_lower_case(func)

    logger.debug(str({"app": app, "func": func, "body": request.body, "query": dict(request.GET)}))

    try:
        obj_app = __import__("%s.views" % app)
        obj_view = getattr(obj_app, 'views')
        obj_cls_list = [getattr(obj_view, cls) for cls in obj_view.__all__]
        obj_func = None

        for obj_cls in obj_cls_list:
            if hasattr(obj_cls, func):
                obj_func = getattr(obj_cls, func)
                break
        if obj_func:
            return obj_func(request)
        else:
            return NotFound()

    except ImportError as e:
        return ServerErr('Import error, Exception:{}'.format(e))

    except Exception as e:
        return ServerErr(e)