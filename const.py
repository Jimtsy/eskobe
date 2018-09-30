# -*- coding: utf-8 -*-
from functools import wraps, lru_cache


class HTTPStatusCode:
    SERVICE_ERROR = 500
    NOT_FOUND = 404
    SUCCESS = 200
    CLIENT_ERROR = 400


class HTTPMethod:
    GET = "GET"
    POST = "POST"


class APPPush:
    class PushType:
        JRON_RPC_PUSH = "1"
        __all__ = [JRON_RPC_PUSH]