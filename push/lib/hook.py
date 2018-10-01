import threading
import queue
from abc import ABCMeta, abstractmethod
from log import logger


class AbstractHook(threading.Thread, metaclass=ABCMeta):
    def __init__(self, name, *args, **kwargs):
        super().__init__(daemon=True, *args, **kwargs)
        self.name = name
        self.queue = queue.Queue(maxsize=10000)
        self.is_running = threading.Event()
        self._destroy = False
        self.get_timeout = 30

    def stop(self):
        logger.info("stop {}".format(self.name))
        self.is_running.clear()

    def resume(self):
        logger.info("resume {}".format(self.name))
        self.is_running.set()

    def destroy(self):
        self._destroy = True

    def is_stop(self):
        if self.is_running.is_set():
            return False
        return True

    def is_destroy(self):
        if self._destroy:
            return True
        return False

    @abstractmethod
    def receive(self, model):
        self.queue.put(model, block=False, timeout=self.get_timeout)

    @abstractmethod
    def run(self):
        self.is_running.set()