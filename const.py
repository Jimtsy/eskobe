# -*- coding: utf-8 -*-


class HTTPStatusCode:
    SERVICE_ERROR = 500
    NOT_FOUND = 404
    SUCCESS = 200
    CLIENT_ERROR = 400
    BIZ_ERROR = 405


class HTTPMethod:
    GET = "GET"
    POST = "POST"


class APPPush:
    class PushType:
        JRON_RPC_PUSH = "1"
        __all__ = [JRON_RPC_PUSH]

    class PushPlatform:
        IOT = "IOT"
        __all__ = [IOT]
