from abc import ABCMeta, abstractmethod
from const import APPPush


class _BaseParser(metaclass=ABCMeta):
    """ response解析规则 """
    def __init__(self, platform, response_time, target_id, *arg, **kwargs):
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


class BasePushBody:
    """PushCenter 推送实体"""
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def decorated(self):
        """body封装"""
        return ""

    def __str__(self):
        return str(self.decorated)

    __repr__ = __str__


class IOTResponseParser(_BaseParser):
    """云喇叭推送实体"""
    def __init__(self, platform, response_time, response, target_id, *args, **kwargs):
        super().__init__(platform=platform, response_time=response_time, target_id=target_id,  *args, **kwargs)
        self.response = response

    @property
    def is_success(self):
        if self.response.__contains__("result"):
            return True
        return False


def new_response_parser(platform, response_time: int, response, target_id):
    if platform == APPPush.PushCenter.IOT:
        return IOTResponseParser(APPPush.PushCenter.IOT, response_time, response, target_id)
    return None

