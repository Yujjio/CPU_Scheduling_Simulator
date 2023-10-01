import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import math
import numpy


class Process:
    def __init__(self, arrival_time, num_burst, name, lambda_, alpha):
        self.alpha = alpha
        self.arrival_time = arrival_time
        self.num_burst = num_burst
        self.type = 1  # 0 for CPU-bound, 1 for IO-bound
        self.type_str = "I/O-bound"
        self.name = chr(name + 65)
        self.burst_num = 0
        self.cpu_burst = []
        self.io_burst = []
        self.tau = math.ceil(1 / lambda_)
        self.old_tau = 0
        self.remain_tau = 0  # remaining prediction time of current cpu burst  SRT
        self.remain_burst_time = 0  # remaining time of current cpu burst  SRT
        self.current_burst = 0  # SRT
        self.wait_start = 0
        self.total_wait_time = 0
        self.total_io_time = 0
        self.turnaround_time = 0
        self.total_cpu_time = 0

    def SetTypeCPU(self):
        self.type = 0
        self.type_str = "CPU-bound"

    def AddCPUBurst(self, burst):
        self.burst_num += 1
        self.cpu_burst.append(burst)
        self.total_cpu_time += burst

    def AddIOBurst(self, burst):
        self.io_burst.append(burst)
        self.total_io_time += burst

    def PopCPUBurst(self, is_srt=False):
        self.burst_num -= 1
        self.old_tau = self.tau
        self.tau = math.ceil(numpy.float32(self.alpha) * numpy.float32(self.cpu_burst[0]) +
                             (1.0 - numpy.float32(self.alpha)) * numpy.float32(self.tau))
        if is_srt:
            self.remain_tau = self.old_tau
            self.remain_burst_time = self.cpu_burst.pop(0)
            self.current_burst = self.remain_burst_time
            return self.current_burst
        return self.cpu_burst.pop(0)

    def RR_PopCPUBurst(self):
        self.burst_num -= 1
        self.remain_burst_time = self.cpu_burst.pop(0)
        self.current_burst = self.remain_burst_time
        return self.current_burst

    def PopIOBurst(self):
        return self.io_burst.pop(0)

    def GetTau(self):
        return self.tau if self.remain_tau <= 0 else self.remain_tau