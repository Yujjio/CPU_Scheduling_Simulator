import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'


class I_O:
    def __init__(self):
        self.queue = {}

    def Add(self, process, time):  # time is the time the process finishes cpu burst and context switch
        out_time = process.PopIOBurst() + time  # time the process finishes io burst
        if out_time in self.queue:
            self.queue[out_time].append(process)
            def sort_func(e):
                return e.name
            self.queue[out_time].sort(key=sort_func)
        else:
            self.queue[out_time] = [process]


    def Pop(self, time):
        return self.queue[time]