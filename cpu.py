import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'


class CPU:
    def __init__(self, t_cs):
        self.process = None
        self.end_time = 0
        self.real_end_time = 0
        self.t_cs = t_cs
        self.count_down = -1  # SRT
        self.next_process = None  # SRT
        self.burst_time = 0  # RR

    def AddProcess(self, process, time, is_srt=False):
        self.process = process
        if is_srt:
            if self.process.remain_burst_time > 0:
                self.end_time = self.process.remain_burst_time + time
                self.real_end_time = self.end_time + self.t_cs
                return True
            self.end_time = process.PopCPUBurst(True) + time  # burst time + current time
        else:
            self.end_time = process.PopCPUBurst() + time
        self.real_end_time = self.end_time + self.t_cs  # burst time + current time + context switch time
        return False

    def RR_AddProcess(self, process, time):
        self.process = process
        if self.process.remain_burst_time > 0:
            self.end_time = self.process.remain_burst_time + time
            self.real_end_time = self.end_time + self.t_cs
            return True
        self.end_time = process.RR_PopCPUBurst() + time
        self.real_end_time = self.end_time + self.t_cs
        self.burst_time = 0
        return False

    def PopProcess(self):
        temp = self.process
        self.process = None
        self.end_time = 0
        self.real_end_time = 0
        self.burst_time = 0
        return temp
