from abc import ABCMeta, abstractmethod


class PushModel(metaclass=ABCMeta):
    """ 抽象实体 """
    def __init__(self, response_time, target_id, platform, *arg, **kwargs):
        super().__init__()
        self._response_time = response_time
        self._target_id = target_id
        self._platform = platform

    @abstractmethod
    def is_success(self) -> bool:
        """是否推送成功"""
        return True

    @property
    def response_time(self) -> int:
        """获取推送响应时间"""
        return self._response_time

    @property
    def platform(self) -> str:
        """获取平台地址"""
        return self._platform

    @property
    def target(self) -> str:
        """获取推送目标ID"""
        return self._target_id


class MOTTModel(PushModel):
    """云喇叭推送实体"""
    def __init__(self, response_time, response, target_id, platform):
        super().__init__(response_time, target_id, platform)
        self.response = response

    @property
    def is_success(self):
        if self.response.__contains__("result"):
            return True
        return False


def new_model(platform, response_time, response, target_id):
    if platform == "mott":
        return MOTTModel(response_time, response, target_id, platform)
    else:
        raise ValueError("not defined")
