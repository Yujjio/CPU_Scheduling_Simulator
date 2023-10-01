import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'


class ReadyQueue:
    def __init__(self, t_cs):
        self.queue = []
        self.length = 0
        self.t_cs = t_cs
        self.count_down = -1

    def __str__(self):
        return "[Q " + " ".join([process.name for process in self.queue]) + "]" if self.queue else "[Q <empty>]"

    def Add(self, process, is_sjf=False):
        self.length += 1
        self.queue.append(process)
        if is_sjf:
            def sort_func(e):
                return [e.tau if e.remain_tau <= 0 else e.remain_tau, e.name]
            self.queue.sort(key=sort_func)

    def Pop(self):
        self.length -= 1
        return self.queue.pop(0)
