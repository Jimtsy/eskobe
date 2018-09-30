# -*- coding: utf-8 -*-

import glob

try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json


class Invoker:
    service = None
    method = None
    request = None
    thread_name = None

    @classmethod
    def from_dict(cls, d):
        inst = cls()
        inst.service = d['declaringClass'].split(".")[-1]
        inst.method = d['method']
        inst.request = {
            "jsonrpc": "2.0",
            "method": inst.method,
            "params": d['arguments'],
            "id": 0
        }
        inst.thread_name = d['thread_name']
        return inst

    def is_response(self, response):
        if response['thread_name'] == self.thread_name:
            return True
        return False

    def __unicode__(self):
        return "{}::{}".format(self.service, self.method)

    def __str__(self):
        return self.__unicode__()

    def __eq__(self, other):
        return str(self) == str(other) if isinstance(other, self.__class__) else False


class Stats:

    def __init__(self, service, method):
        self.service = service
        self.method = method
        self.counts = 0

    def __unicode__(self):
        return "{}::{} - {}".format(self.service, self.method, self.counts)

    def __str__(self):
        return self.__unicode__()

    def receive(self, invoker):
        self.counts += 1

    def uuid(self):
        return "{}::{}".format(self.service, self.method)


class Parser:

    def __init__(self, fp=None, path_re=None):
        self.file = fp
        self.path_re = path_re
        self.stats = dict()
        self.buffer = []

    def handle_start_msg(self, d):
        invoker = Invoker.from_dict(d)
        self.buffer.append(invoker)

    def handle_end_msg(self, d):
        for index, b in enumerate(self.buffer):
            if b.is_response(d):
                self.buffer.pop(index)
                if str(b) not in self.stats:
                    stats = Stats(b.service, b.method)
                    self.stats[stats.uuid()] = stats
                self.stats[str(b)].receive(b)
                break
        else:
            print("no matched invoker found")

    def parse(self):
        if self.file is not None:
            files = [self.file]
        else:
            assert self.path_re
            files = glob.glob(self.path_re)

        for file in files:
            print("parsing file: {}".format(file))
            with open(file, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    try:
                        d = json.loads(line, encoding='utf-8')
                    except ValueError as e:
                        print(str(e))
                        continue
                    msg = d.get('message')
                    if msg == "invoking service method start":
                        self.handle_start_msg(d)
                    elif msg == "invoking service method end":
                        self.handle_end_msg(d)

        # for _, v in self.stats.items():
        #     print(str(v))
        apis = list(self.stats.values())
        apis.sort(key=lambda r: r.counts, reverse=True)
        print("|service|method|调用量|\n|---|---|---|\n")
        print("\n".join(["{}|{}|{}".format(api.service, api.method, api.counts) for api in apis]))


if __name__ == "__main__":
    Parser(fp="main-2018-09-14.86.log").parse()