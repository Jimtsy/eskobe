# -*- coding: utf-8 -*-
import threading
import queue
import requests
from log import logger


class InfluxDBHelper(threading.Thread):
    def __init__(self,
                 host="http://106.14.30.88",
                 port=8086,
                 user="admin",
                 password="admin123",
                 database="easysite",
                 measurement="push"):

        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=10000)
        self.session = requests.session()
        self.url = "{host}:{port}/write?db={db}&u={user};&p={psw}".format(host=host, port=port, db=database, user=user, psw=password)
        self.measurement = measurement

    def receive(self, model):
        if model.is_success:
            self.queue.put(model, block=False, timeout=1)

    def write_point(self, measurement):
        logger.info("influx_hooks starting...")
        while True:
            model = self.queue.get()
            point = "{measurement},target={target},platform={platform} response_time={response_time}".format(
                measurement=measurement,
                target=model.target,
                platform=model.platform,
                response_time=int(model.response_time)
            )
            resp = self.session.post(self.url, data=point)
            if resp.text != "":
                logger.error("failed to insert to influx, {}".format(resp.text))

    def run(self):
        self.write_point(self.measurement)


Influx_hook = InfluxDBHelper()