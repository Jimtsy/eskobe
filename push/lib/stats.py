import threading
import time
import queue
from log import logger


class StatsHook(threading.Thread):
    def __init__(self, show_rhythm=3):
        super().__init__(daemon=True)
        self.requests = 0
        self.failures = 0
        self.min = 0
        self.max = 0
        self.average = 0
        self.queue = queue.Queue(maxsize=10000)
        self.total_response_time = 0
        self.show_rhythm = show_rhythm
        self.__is_print = threading.Event()
        self.__is_print.set()
        self.get_timeout = 10
        self.lock = threading.Condition()

    def reset(self):
        self.lock.acquire()
        self.requests = 0
        self.failures = 0
        self.min = 0
        self.max = 0
        self.average = 0
        self.total_response_time = 0
        self.lock.release()

    def update_min(self, response_time):
        self.min = response_time if response_time < self.min or self.min == 0 else self.min

    def update_max(self, response_time):
        self.max = response_time if response_time > self.max else self.max

    def run(self):
        logger.info("stats_hooks starting...")

        show_stats = threading.Thread(target=self.show_stats, daemon=False, args=(self.show_rhythm, ))
        show_stats.start()

        while True:
            try:
                rp = self.queue.get(timeout=self.get_timeout)
            except queue.Empty:
                if not self.__is_print.is_set():
                    continue
                else:
                    self.stop()
            else:
                self.lock.acquire()
                if not self.__is_print.is_set():
                    self.resume()
                self.requests += 1
                self.total_response_time += rp.response_time
                self.update_min(rp.response_time)
                self.update_max(rp.response_time)
                if not rp.is_success:
                    self.failures += 1
                self.lock.release()

    def receive(self, model):
        """必须是线程安全的"""
        self.queue.put(model, block=False, timeout=2)

    def show_stats(self, response_time):
        while True:
            if self.__is_print.is_set():
                logger.info(str(self.json_stats()))
                time.sleep(response_time)

    def json_stats(self):
        return dict(
            requests=self.requests,
            failures=self.failures,
            failures_rate=0 if self.failures == 0 else "%.2f" % (self.failures / self.requests * 100) + "%",
            average=0 if self.requests == 0 else int(self.total_response_time / self.requests),
            min=int(self.min),
            max=int(self.max)
        )

    def stop(self):
        logger.info("stop print")
        self.__is_print.clear()

    def resume(self):
        logger.info("resume print")
        self.__is_print.set()

    @property
    def current_stats(self):
        return self.json_stats()