# -*- coding: utf-8 -*-

import threading
import django.http as response
import timeit
from log import logger
from collections import defaultdict, OrderedDict
from functools import wraps

try:
    import simplejson as json
except ImportError:
    import json


class Proxy(object):
    def __init__(self, obj):
        self._obj = obj

    def __setattr__(self, key, value):
        if key == "_obj":
            super().__setattr__(key, value)
        else:
            setattr(self._obj, key, value)

    def __getattr__(self, item):
        return getattr(self._obj, item)


class SingleInstance():
    def __init__(self):
        pass


class GlobalCount(object):
    def __init__(self, start=0):
        self.count = start
        self.cd = threading.Condition()

    @property
    def auto_add(self):
        self.cd.acquire()
        self.count += 1
        self.cd.release()
        return self.count

    @property
    def current(self):
        self.cd.acquire()
        c = self.count
        self.cd.release()
        return c

    def update(self, count):
        self.cd.acquire()
        self.count += count
        self.cd.release()
        return self.count


class GlobalCache(object):
    def __init__(self, name, size=100):
        self.name = name
        self.cd = threading.Condition()
        self._cache = {"name": name}

    @property
    def put(self, **kwargs):
        self.cd.acquire()
        for k, v in kwargs.items():
            self._cache[k] = v


def camel_case_to_lower_case(name):
    """ upayNotify -> upay_notify

    :param name:
    :return:
    """
    new = ''
    for c in name:
        if c in "ABCDEFGHIJKMLNOPQRSTUVWXYZ":
            c = "_"+c.lower()
        new += c
    return new


def make_sequence_key(*args, **kwargs):
    """ 根据传入的参数，生成一个唯一的key

    :param args:
    :param kwargs:
    :return:
    """
    args = list(map(lambda s: str(s), args))
    args.sort()
    k1 = "".join(arg for arg in args)
    k2 = "".join([str(k) + str(v) for k, v in sorted(kwargs.items())])
    return k1 + k2


def cache_request_params(size=100):
    """ 根据函数名称增加请求接口的缓存，并控制缓存的大小

    :param size: 每个函数设置的缓存大小
    :param lock: 并发时需要传入全局锁
    :return:
    """
    _cache = defaultdict(OrderedDict)

    def wrapper(func):
        name = func.__name__

        def _wrap(req):
            b = q = ""
            if req.body != b'':
                body = json.loads(str(req.body, encoding="utf-8"))
                b = str(sorted(body.items(), key=lambda item: item[0]))
            if req.GET != {}:
                q = str(sorted(req.GET.items(), key=lambda item: item[0]))
            k = b + q

            if k not in _cache.get(name, {}):
                ret = func(req)
                _cache[name][k] = ret
                return ret

            li = list(_cache[name].keys())
            logger.info("has cached, len: {}".format(len(li)))
            if len(li) > size:
                del _cache[name][li[0]]

            return _cache[name][k]
        return _wrap
    return wrapper


def allow_method(allowed_method: list):
    def wrapper(func):
        @wraps(func)
        def _wrap(req):
            if req.method not in allowed_method:
                return response.HttpResponseNotFound("Bad Request")
            return func(req)
        return _wrap
    return wrapper


def general_cached(func):
    cached = {}

    @wraps(func)
    def wrap(*args, **kwargs):
        k = make_sequence_key(args, kwargs)
        if k in cached:
            return cached[k]
        ret = func(*args, **kwargs)
        cached[k] = ret
        return ret
    return wraps


def echo_request_params(func):
    """ 打印请求参数，用于调试

    :param func:
    :return:
    """
    def wrap(*args, **kwargs):
        logger.info("args: {}, kwargs: {}".format(args, kwargs))
        func(*args, **kwargs)
    return wrap


def function_runtime(func):
    """

    :param func:
    :return: response, millisecond
    """
    def wrap(*args, **kwargs):
        start = timeit.default_timer()
        ret = func(*args, **kwargs)
        return ret, (timeit.default_timer() - start) * 1000
    return wrap
