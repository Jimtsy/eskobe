# -*- coding: utf-8 -*-

import requests
import threading
import time
import random
from utils import function_runtime, make_sequence_key
from push.lib.hook_stats import StatsHook
from push.lib.hook_influxdb import InfluxDBHelper
from const import APPPush
from log import logger


class PPPool(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._instance = {}
        cls.condition = threading.Condition()

    def __call__(cls, *args, **kwargs):
        k = make_sequence_key(*args, **kwargs)
        if k not in cls._instance:
            inst = super().__call__(*args, **kwargs)
            cls._instance[k] = inst
        return cls._instance[k]


class PushPlatform(metaclass=PPPool):
    # todo: 推送平台是单实例，但是根据推送的目标不通，可以生成多个目标统计，与目标influxdb。
    def __init__(self, platform, response_parser_callback, push_address, *args, **kwargs):
        self.push_address = push_address
        self.session = requests.session()
        self.platform = platform
        self.stats_hooks = {}
        self.influx_db_hooks = {}
        self.response_parser_callback = response_parser_callback

    @function_runtime
    def __call_(self, method, url, **kwargs):
        return self.session.request(method=method, url=url, **kwargs)

    def _push(self, method, url, target_id, latency, jitter, **kwargs):
        response, response_time = self.__call_(method, url, **kwargs)
        rpc = self.response_parser_callback(response_time, response.text, target_id)

        if target_id in self.stats_hooks:
            self.stats_hooks[target_id].receive(rpc)
            self.influx_db_hooks[target_id].receive(rpc)

        st = random.randint(latency - jitter, latency + jitter)
        time.sleep(st/1000)
        
    def clear_hook(self, target_id):
        logger.info("clear_hook {}".format(target_id))
        self.stats_hooks[target_id].destroy()
        self.influx_db_hooks[target_id].destroy()
        del self.stats_hooks[target_id]
        del self.influx_db_hooks[target_id]

    def start_hook(self, target_id):
        logger.info("start_hook {}".format(target_id))
        self.stats_hooks[target_id].start()
        self.influx_db_hooks[target_id].start()

    def add_hook(self, target_id):
        logger.info("add_hook {}".format(target_id))
        if target_id not in self.stats_hooks:
            self.stats_hooks[target_id] = StatsHook(target_id)
        else:
            if self.stats_hooks[target_id].is_stop():
                self.stats_hooks[target_id].resume()

        if target_id not in self.influx_db_hooks:
            self.influx_db_hooks[target_id] = InfluxDBHelper(target_id)
        else:
            if self.influx_db_hooks[target_id].is_stop():
                self.influx_db_hooks[target_id].resume()

    def show_hooks(self):
        summary = {
            "stats_hook": {},
            "influx_db_hook": {}
        }

        for target_id, hook in self.stats_hooks.items():
            summary["stats_hook"][target_id] = hook.is_stop() is False

        for target_id, hook in self.influx_db_hooks.items():
            summary["influx_db_hook"][target_id] = hook.is_stop()  is False

        return summary

    def _foolish_push(self, method, url, target_id, **kwargs):
        """ 循环推送

        :param method:
        :param url:
        :param target_id:
        :param kwargs:
        :return:
        """
        while True:
            # 如果不存在就说明已经停止了
            if target_id not in self.stats_hooks:
                break
            self._push(method, url, target_id, **kwargs)

    def _smart_push(self, method, url, counts, target_id, **kwargs):
        """ 限制次数推送

        :param method:
        :param url:
        :param counts:
        :param target_id:
        :param kwargs:
        :return:
        """
        for _ in range(counts):
            # 如果不存在就说明已经停止了
            if target_id not in self.stats_hooks:
                break
            self._push(method, url, target_id, **kwargs)

    def __make_json_rpc_payload(self, api, body):
        return dict(method=api, jsonrpc="2.0", id="0", params=body.decorated)

    def _json_rpc_push(self, api, body, push_count, **kwargs):

        payload = self.__make_json_rpc_payload(api, body)

        if push_count == 0:
            kwargs["json"] = payload
            concurrency = kwargs.pop("concurrency", 1)
            thread_pool = [threading.Thread(target=self._foolish_push,
                                            args=("post", self.push_address, body.target_id),
                                            kwargs=kwargs) for _ in range(concurrency)]
            [t.setDaemon(True) for t in thread_pool]
            [t.start() for t in thread_pool]

        else:
            kwargs["json"] = payload
            kwargs.pop("concurrency")
            thread = threading.Thread(target=self._smart_push,
                                      args=("post", self.push_address, push_count, body.target_id),
                                      kwargs=kwargs)
            thread.setDaemon(False)
            thread.start()

    def start_push(self, push_type, api, body, **kwargs):
        if push_type not in APPPush.PushType.__all__:
            return "未定义, 目前支持 {}".format(APPPush.PushType.__all__)
        
        jitter = kwargs.get("jitter", 0)
        latency = kwargs.get("latency", 1000)
        if latency < jitter:
            return "latency 必须小于 jitter"

        concurrency = kwargs.get("concurrency", 1)
        push_count = kwargs.get("push_count", 0)

        # 加载hooks
        self.add_hook(body.target_id)
        if not self.stats_hooks[body.target_id].is_stop():
            return "{} 已经启动推送: {}".format(self.platform, body.target_id)
        else:
            self.start_hook(body.target_id)

        if push_type == "1":
            self._json_rpc_push(api=api, body=body, push_count=push_count,
                                concurrency=concurrency, latency=latency, jitter=jitter)
        return "查看实时统计信息: http://xxx:3000/dashboard/db/shou-qian-ba-tui-song?" \
               "panelId=1&fullscreen&edit&from=now-5m&to=now&tab=metrics"

    def stop_push(self, target_id):
        """ 需要停止所有的hook即可

        :param target_id:
        :return:
        """
        if target_id in self.stats_hooks:
            if self.stats_hooks[target_id].is_destroy():
                return "already destroy"
            else:
                self.clear_hook(target_id)
        else:
            return "{} 未向目标ID: {} 发起推送".format(self.platform, target_id)
        return "OK"

    def show_stats(self, target_id):
        if target_id in self.stats_hooks:
            return self.stats_hooks[target_id].current_stats
        return "{} 未向目标ID: {} 发起推送".format(self.platform, target_id)


class MOTTPushPlatform(PushPlatform):
    """云喇叭推送"""
    def __init__(self, response_parser_callback, push_address):
        super().__init__(APPPush.PushPlatform.IOT, response_parser_callback, push_address)

    def start_push(self, body, **kwargs):
        return super().start_push("1", "pushTemplateMessage", body, **kwargs)