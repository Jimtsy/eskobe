# -*- coding: utf-8 -*-

from push.lib.platform import MOTTPushPlatform
from push.lib.parser import IOTResponseParser
from push.lib.body import IOTPushBody
from functools import lru_cache
from const import APPPush


class PushCenter:
    def __init__(self):
        self.push_platform = {}

    def _collect(self, push_platform):
        if push_platform.platform not in self.push_platform:
            self.push_platform[push_platform.platform] = push_platform

    @lru_cache(maxsize=None)
    def _new_push_platform(self, platform):
        if platform == APPPush.PushPlatform.IOT:
            callback = lambda *args, **kwargs: IOTResponseParser(*args, **kwargs)
            push_platform = MOTTPushPlatform(callback, "")
            self._collect(push_platform)
            return push_platform
        return None

    @lru_cache(maxsize=None)
    def new_push_body(self, platform, app_id, app_key, amount, target_id, **kwargs):
        """ 缓存推送实体

        :param platform:
        :param args:
        :param kwargs:
        """
        if platform == APPPush.PushPlatform.IOT:
            return IOTPushBody(platform=platform, app_id=app_id, app_key=app_key, amount=amount, target_id=target_id, **kwargs)
        return None

    def push(self, platform, body):
        pp = self._new_push_platform(platform)
        if not pp:
            return "not defined {}, maybe you need select from {}".format(platform, APPPush.PushPlatform.__all__)
        return pp.start_push(body)

    def kill_push(self, platform, target_id):
        if platform in self.push_platform:
            return self.push_platform[platform].stop_push(target_id)
        return "no push need to kill, pushing platform is {}".format(self.push_platform.keys())

    def show_stats(self, platform, target_id):
        if platform in self.push_platform:
            return self.push_platform[platform].show_stats(target_id)
        return "has not found running {}, pushing platform is {}".format(platform, list(self.push_platform.keys()))

    def show_hooks(self, platform):
        if platform in self.push_platform:
            return self.push_platform[platform].show_hooks()
        return "has not found running {}, pushing platform is {}".format(platform, list(self.push_platform.keys()))

push_center = PushCenter()
