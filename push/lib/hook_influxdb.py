# -*- coding: utf-8 -*-
import queue
import requests
import threading
from log import logger
from push.lib.hook import AbstractHook


class InfluxDBHelper(AbstractHook):
    def __init__(self, name,
                 host="http://106.14.30.88",
                 port=8086,
                 user="admin",
                 password="admin123",
                 database="easysite",
                 measurement="push"):
        super().__init__(name)
        self.name = "influx_db_" + name
        self.session = requests.session()
        self.url = "{host}:{port}/write?db={db}&u={user};&p={psw}".format(host=host, port=port, db=database, user=user, psw=password)
        self.measurement = measurement
        self.queue = queue.Queue(maxsize=10000)
        self.is_running = threading.Event()
        self._destroy = False

    def receive(self, model):
        if model.is_success:
            self.queue.put(model, block=False, timeout=1)

    def write_point(self, measurement):
        logger.info("influx_hooks starting...")
        while True:
            try:
                model = self.queue.get(timeout=self.get_timeout)
            except queue.Empty:
                if self._destroy:
                    logger.info("{} destroyed".format(self.name))
                    break
                if self.is_stop():
                    continue
                else:
                    self.stop()
            else:
                if self.is_stop():
                    self.resume()
                point = "{measurement},target={target},platform={platform} response_time={response_time}".format(
                    measurement=measurement,
                    target=model.target,
                    platform=model.platform,
                    response_time=model.response_time
                )
                resp = self.session.post(self.url, data=point)
                if resp.text != "":
                    logger.error("failed to insert to influx, {}".format(resp.text))

    def run(self):
        super().run()
        self.write_point(self.measurement)
