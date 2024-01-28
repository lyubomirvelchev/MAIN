import heapq


class CallbackList:
    cb_list = []

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)

    def attach(self, o):
        if o not in self.cb_list:
            self.cb_list.append(o)

    def detach(self, o):
        if o in self.cb_list:
            self.cb_list.remove(o)

    def clear(self):
        self.cb_list = []

    def call(self, *args, **kwargs):
        for o in self.cb_list:
            o(*args, **kwargs)


class PriorityCallbackList:
    cb_list = []

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)

    def attach(self, o, priority=0):
        if (priority, o) not in self.cb_list:
            heapq.heappush(self.cb_list, (priority, o))

    def detach(self, o):
        new_list = []
        for priority, elem in heapq.nsmallest(len(self.cb_list), self.cb_list):
            if o is not elem:
                heapq.heappush(new_list, (priority, elem))
        self.cb_list = new_list

    def clear(self):
        self.cb_list = []

    def call(self, *args, **kwargs):
        for _, o in heapq.nsmallest(len(self.cb_list), self.cb_list):
            o(*args, **kwargs)


if __name__ == "__main__":
    c = PriorityCallbackList()
    asd = lambda x: print('asdf')


    c.attach(asd, priority=1)
    c.attach(lambda x: print(x))

    c.attach(lambda x: print(x + 10), priority=10)
    c.call(4)

    c.detach(asd)
    c(234)
    c.clear()
    c(2)
