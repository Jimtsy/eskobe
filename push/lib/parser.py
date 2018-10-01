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


class IOTResponseParser(_BaseParser):
    """云喇叭推送实体"""
    def __init__(self, response_time, response, target_id, *args, **kwargs):
        super().__init__(platform=APPPush.PushPlatform.IOT, response_time=response_time, target_id=target_id,  *args, **kwargs)
        self.response = response

    @property
    def is_success(self):
        if self.response.__contains__("result"):
            return True
        return False
