# -*- coding: utf-8 -*-
import requests
import threading
import time
import random
import ctypes
import inspect
from utils import function_runtime, make_sequence_key
from push.lib.stats import StatsHook
from push.lib.influxdb import InfluxDBHelper, Influx_hook
from push.lib.model import new_model
from log import logger


class Body:
    """PushCenter 推送实体"""
    def __init__(self, app_id, app_key, temple_id, amount: int, target_id, platform="IOT", priority: int=1):
        self.app_id = app_id
        self.app_key = app_key
        self.temple_id = temple_id
        self.amount = amount
        self.target_id = target_id
        self.platform = platform
        self.priority = priority

    @property
    def decorated(self):
        return [
            self.app_id,
            self.app_key,
            self.temple_id,
            dict(amount=self.amount),
            [self.target_id],
            self.platform,
            self.priority,
        ]

    def __str__(self):
        return str(self.decorated)

    __repr__ = __str__


class PCPool(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._instance = {}
        cls.condition = threading.Condition()

    def __call__(cls, *args, **kwargs):
        k = make_sequence_key(*args, **kwargs)
        if k not in cls._instance:
            inst = super().__call__(*args, **kwargs)
            stats_hook = StatsHook()
            inst.add_handle_function_stats(stats_hook)
            inst.add_handle_function_influx_db(Influx_hook)
            cls._instance[k] = inst
        return cls._instance[k]


class PushCenter(metaclass=PCPool):
    def __init__(self, platform):
        self.push_address = "http://pushservice-core.test.shouqianba.com/rpc/push"
        self.session = requests.session()
        self.stats_hook = None
        self.influx_bd_hook = None
        self.platform = platform
        self.hooks = {}
        self.stop_push = False

    def add_handle_function_stats(self, sh: StatsHook):
        if "stats" in self.hooks:
            return
        self.stats_hook = sh
        self.hooks["stats"] = sh

    def add_handle_function_influx_db(self, ih: InfluxDBHelper):
        if "influx" in self.hooks:
            return
        self.hooks["influx"] = ih

    @function_runtime
    def __push(self, method, url, **kwargs):
        return self.session.request(method=method, url=url, **kwargs)

    def _push(self, method, url, target_id, latency, jitter, **kwargs):
        response, response_time = self.__push(method, url, **kwargs)
        model = new_model(self.platform, response_time, response.text, target_id)

        if self.hooks:
            [hook.receive(model) for _, hook in self.hooks.items() if hook.is_alive()]

        st = random.randint(latency - jitter, latency + jitter)
        time.sleep(st/1000)

    def foolish_push(self, method, url, target_id, **kwargs):
        """ 循环推送

        :param method:
        :param url:
        :param target_id:
        :param kwargs:
        :return:
        """
        while True:
            if self.stop_push:
                break
            self._push(method, url, target_id, **kwargs)

    def smart_push(self, method, url, counts, target_id, **kwargs):
        """ 限制次数推送

        :param method:
        :param url:
        :param counts:
        :param target_id:
        :param kwargs:
        :return:
        """
        for _ in range(counts):
            if self.stop_push:
                break
            self._push(method, url, target_id, **kwargs)

    def __make_json_rpc_payload(self, api, body: Body):
        return dict(method=api, jsonrpc="2.0", id="0", params=body.decorated)

    def _json_rpc_push(self, api, body: Body, push_count, **kwargs):

        payload = self.__make_json_rpc_payload(api, body)

        if push_count == 0:
            kwargs["json"] = payload
            concurrency = kwargs.pop("concurrency", 1)
            thread_pool = [threading.Thread(target=self.foolish_push,
                                            args=("post", self.push_address, body.target_id),
                                            kwargs=kwargs) for _ in range(concurrency)]
            [t.setDaemon(True) for t in thread_pool]
            [t.start() for t in thread_pool]

        else:
            kwargs["json"] = payload
            kwargs.pop("concurrency")
            thread = threading.Thread(target=self.smart_push,
                                      args=("post", self.push_address, push_count, body.target_id),
                                      kwargs=kwargs)
            thread.setDaemon(False)
            thread.start()

    def start_push(self, push_type, api, body: Body, **kwargs):

        jitter = kwargs.get("jitter", 0)
        latency = kwargs.get("latency", 1000)

        if latency < jitter:
            raise ValueError

        concurrency = kwargs.get("concurrency", 1)
        push_count = kwargs.get("push_count", 0)

        if self.hooks:
            [hook.start() for _, hook in self.hooks.items() if not hook.is_alive()]

        if push_type == "1":
            self._json_rpc_push(api=api, body=body, push_count=push_count, concurrency=concurrency, latency=latency, jitter=jitter)

    def stop_all_thread(self):
        if self.stop_push:
            return "already stop"

        self.stop_push = True
        return "OK"

    def show_stats(self):
        if self.stats_hook:
            return self.stats_hook.current_stats
        return None


if __name__ == "__main__":
    b = Body(app_id="d2c8f66a91a8b35026efc0e1d88faeca",
             app_key="0cbf80acfb836b31ae7afddf6f1e9425",
             temple_id="5b14eded5c40450001b056e2",
             target_id="070c4897-f457-43f1-bafc-1541bce94ab61",
             amount=1)

    pc = PushCenter(platform="mott")
    pc.start_push("1","pushTemplateMessage", b, push_count=0, concurrency=1)
    pc.stop_all_thread()