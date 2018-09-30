# -*- coding: utf-8 -*-

from django.http import JsonResponse
from const import HTTPStatusCode
from log import logger


def new_response_data(error, detail):
    return {"result": error, "detail": detail}


class BaseJSONNotifyResponse(JsonResponse):
    def __init__(self, data, safe=False, status=HTTPStatusCode.SUCCESS, **kwargs):
        if isinstance(data, dict):
            data = dict(status_code=status, response=data)
        else:
            data = dict(status_code=status, response="{}".format(data))
        super().__init__(data=data, safe=safe, **kwargs)


class ParamsErrorResponse(BaseJSONNotifyResponse):
    def __init__(self, detail=None):
        _data = new_response_data("parameters error", detail)
        logger.error(_data)
        super().__init__(_data, status=HTTPStatusCode.CLIENT_ERROR)


class SuccessResponse(BaseJSONNotifyResponse):
    def __init__(self, detail=None):
        _data = new_response_data("success", detail)
        logger.info(_data)
        super().__init__(_data, status=HTTPStatusCode.SUCCESS)


class ServerErrorResponse(BaseJSONNotifyResponse):
    def __init__(self, detail=None):
        _data = new_response_data("interval server 500", detail)
        logger.error(detail)
        super().__init__(_data, status=HTTPStatusCode.SERVICE_ERROR)


class NotFoundResponse(BaseJSONNotifyResponse):
    def __init__(self, detail=None):
        _data = new_response_data("404 not found", detail)
        logger.error(detail)
        super().__init__(_data, status=HTTPStatusCode.NOT_FOUND)