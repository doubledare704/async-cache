from collections import OrderedDict
from copy import deepcopy


class LRU(OrderedDict):
    def __init__(self, maxsize, *args, **kwargs):
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        value = deepcopy(super().__getitem__(key))
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, deepcopy(value))
        if self.maxsize and len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
