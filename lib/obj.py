import json
import collections


def any2obj(ref):
    return json2obj(json.dumps(ref))


def json2obj(data):
    return json.loads(data,
                      object_hook=lambda d:
                      collections.namedtuple('_', d.keys())(*d.values()))


class objectview(object):

    def __init__(self, d):
        self.__dict__ = d
