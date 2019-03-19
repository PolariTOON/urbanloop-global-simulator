import copy


class Queue:
    def __init__(self, maxsize=0):
        self._maxsize = maxsize
        self._is_bounded = False
        self.items = []

        if maxsize >= 1:
            self._is_bounded = True

    def get(self):
        if len(self.items) <= 0:
            return None
        return self.items.pop(0)

    def get_no_pop(self):
        if len(self.items) <= 0:
            return None
        return self.items[0]

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)

    def put(self, item):
        if len(self.items) > 0 and type(self.items[0]) is not type(item):
            return None
        if self._is_bounded and self._maxsize <= len(self.items) + 1:
            return None
        return self.items.append(item)

    def qsize(self):
        return len(self.items)

    def list(self):
        return copy.deepcopy(self.items)

    def full(self):
        if not self._is_bounded:
            return False
        return len(self.items) == self._maxsize

    def is_empty(self):
        return len(self.items) == 0

    def empty(self):
        self.items = []
        return

    def index_of(self, item):
        if len(self.items) > 0 and type(self.items[0]) is not type(item):
            return -1
        if item in self.items:
            return self.items.index(item)
        return -1
