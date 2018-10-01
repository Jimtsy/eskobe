from abc import ABCMeta, abstractmethod
from const import APPPush
import random


class _BasePushBody(metaclass=ABCMeta):
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


class IOTPushBody(_BasePushBody):
    """PushCenter 推送实体"""

    def __init__(self, platform, app_id, app_key, temple_id, amount: int, target_id, priority: int = 1):
        super().__init__()
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
