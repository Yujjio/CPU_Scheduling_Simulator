import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from drand48 import Rand48
from process import Process
from ready_queue import ReadyQueue
from i_o import I_O
from cpu import CPU
import sys
import copy
import math


def setup(t_cs):
    return ReadyQueue(t_cs), CPU(t_cs), I_O(), 0, 0


def simout(algo, processes, time, num_context_switch, cpu_bound_context_switch,
           io_bound_context_switch, num_preemptions=0, cpu_bound_preemptions=0, io_bound_preemptions=0):
    time -= 1
    # create simout.txt if not exist, otherwise write the content after the existing content
    with open("simout.txt", "a+") as f:
        result = "Algorithm {}\n".format(algo)
        # wait time
        total_wait_time, total_cpu_burst_num = 0, 0
        cpu_bound_wait_time, cpu_bound_cpu_burst_num = 0, 0
        io_bound_wait_time, io_bound_cpu_burst_num = 0, 0
        # turnaround time
        total_turnaround_time, cpu_bound_turnaround_time, io_bound_turnaround_time = 0, 0, 0
        # cpu_utilization
        total_cpu_burst_time, cpu_bound_cpu_burst_time, io_bound_cpu_burst_time = 0, 0, 0
        for arrival_time in processes:
            for process in processes[arrival_time]:
                total_wait_time += process.total_wait_time
                total_cpu_burst_num += process.num_burst
                total_turnaround_time += process.turnaround_time
                total_cpu_burst_time += process.total_cpu_time
                if process.type == 0:
                    cpu_bound_wait_time += process.total_wait_time
                    cpu_bound_cpu_burst_num += process.num_burst
                    cpu_bound_turnaround_time += process.turnaround_time
                    cpu_bound_cpu_burst_time += process.total_cpu_time
                else:
                    io_bound_wait_time += process.total_wait_time
                    io_bound_cpu_burst_num += process.num_burst
                    io_bound_turnaround_time += process.turnaround_time
                    io_bound_cpu_burst_time += process.total_cpu_time
        # cpu utilization
        cpu_util = math.ceil(total_cpu_burst_time / time * 100000) / 1000
        # cpu_util = total_cpu_burst_time / time * 100
        result += "-- CPU utilization: {:.3f}%\n".format(cpu_util)
        # average CPU burst time
        if total_cpu_burst_num == 0:
            avg_cpu_burst_time = 0
            total_average_wait_time = 0
            total_turnaround_time = 0
        else:
            avg_cpu_burst_time = math.ceil(total_cpu_burst_time / total_cpu_burst_num * 1000) / 1000
            total_average_wait_time = math.ceil(total_wait_time / total_cpu_burst_num * 1000) / 1000  # wait time
            total_average_turnaround_time = math.ceil(total_turnaround_time / total_cpu_burst_num * 1000) / 1000
        if cpu_bound_cpu_burst_num == 0:
            avg_cpu_bound_cpu_burst_time = 0
            cpu_bound_average_wait_time = 0
            cpu_bound_average_turnaround_time = 0
        else:
            avg_cpu_bound_cpu_burst_time = math.ceil(cpu_bound_cpu_burst_time / cpu_bound_cpu_burst_num * 1000) / 1000
            cpu_bound_average_wait_time = math.ceil(cpu_bound_wait_time / cpu_bound_cpu_burst_num * 1000) / 1000
            cpu_bound_average_turnaround_time = math.ceil(
                cpu_bound_turnaround_time / cpu_bound_cpu_burst_num * 1000) / 1000
        if io_bound_cpu_burst_num == 0:
            avg_io_bound_cpu_burst_time = 0
            io_bound_average_wait_time = 0
            io_bound_average_turnaround_time = 0
        else:
            avg_io_bound_cpu_burst_time = math.ceil(io_bound_cpu_burst_time / io_bound_cpu_burst_num * 1000) / 1000
            io_bound_average_wait_time = math.ceil(io_bound_wait_time / io_bound_cpu_burst_num * 1000) / 1000
            io_bound_average_turnaround_time = math.ceil(
                io_bound_turnaround_time / io_bound_cpu_burst_num * 1000) / 1000
        result += "-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n".format(avg_cpu_burst_time,
                                                                                        avg_cpu_bound_cpu_burst_time,
                                                                                        avg_io_bound_cpu_burst_time)
        # wait time
        result += "-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n".format(total_average_wait_time,
                                                                                   cpu_bound_average_wait_time,
                                                                                   io_bound_average_wait_time)
        # turnaround time
        result += "-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)\n".format(total_average_turnaround_time,
                   cpu_bound_average_turnaround_time, io_bound_average_turnaround_time)
        # context switch
        result += "-- number of context switches: {} ({}/{})\n".format(num_context_switch, cpu_bound_context_switch,
                                                                       io_bound_context_switch)
        # preemption
        result += "-- number of preemptions: {} ({}/{})\n".format(num_preemptions,
                                                                  cpu_bound_preemptions, io_bound_preemptions)
        if algo != "RR":
            result += '\n'
        f.write(result)


def fcfs_sjf(processes, t_cs, total_process_num, is_sjf=False):
    if is_sjf:
        print("time 0ms: Simulator started for SJF [Q <empty>]")
    else:
        print("time 0ms: Simulator started for FCFS [Q <empty>]")
    queue, cpu, io, time, finish_num = setup(t_cs)
    num_context_switch, cpu_bound_context_switch, io_bound_context_switch = 0, 0, 0
    while finish_num < total_process_num:
        have_added = False
        if queue.length <= 0 and time in processes:  # process arrives
            have_added = True
            for process in processes[time]:
                process.wait_start = time
                if is_sjf:
                    queue.Add(process, True)
                else:
                    queue.Add(process)
                if time < 10000:
                    if is_sjf:
                        print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(time,
                                                                                    process.name, process.tau, queue))
                    else:
                        print("time {}ms: Process {} arrived; added to ready queue {}".format(time, process.name,
                                                                                              queue))

        if cpu.process and cpu.end_time == time:  # process finishes cpu burst
            num_context_switch += 1
            if cpu.process.type == 0:
                cpu_bound_context_switch += 1
            else:
                io_bound_context_switch += 1
            if cpu.process.burst_num == 0:  # process finishes
                print("time {}ms: Process {} terminated {}".format(time, cpu.process.name, queue))
            else:
                if time < 10000:
                    if is_sjf:
                        print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} {} to go {}".format(time,
                              cpu.process.name, cpu.process.old_tau, cpu.process.burst_num,
                              'bursts' if cpu.process.burst_num > 1 else 'burst', queue))
                        print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms {}".format(
                                time, cpu.process.name, cpu.process.old_tau, cpu.process.tau, queue))
                    else:
                        print("time {}ms: Process {} completed a CPU burst; {} {} to go {}".format(time,
                              cpu.process.name, cpu.process.burst_num,
                              "bursts" if cpu.process.burst_num > 1 else "burst", queue))
                    print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms {}".format(time,
                          cpu.process.name, time + cpu.process.io_burst[0] + t_cs, queue))
        elif cpu.process and cpu.real_end_time == time:  # process finishes cpu burst and context switch
            process = cpu.PopProcess()
            if process.burst_num == 0:
                finish_num += 1
                process.turnaround_time = time - process.arrival_time - process.total_io_time
                # print("--turnaround time: {}ms".format(process.turnaround_time))
            else:
                io.Add(process, time)

        if queue.queue and not cpu.process and queue.count_down == -1:  # push process to cpu, start context switch
            queue.count_down = t_cs
            queue.queue[0].total_wait_time += time - queue.queue[0].wait_start
            queue.queue[0].wait_start = time
        elif queue.count_down > 0:  # context switch is still going
            if queue.count_down == t_cs:
                cpu.next_process = queue.Pop()
            queue.count_down -= 1

        if queue.count_down == 0:  # context switch finishes, push process to cpu
            process = cpu.next_process
            cpu.next_process = None
            cpu.AddProcess(process, time)
            if time < 10000:
                if is_sjf:
                    print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst {}".format(time,
                          process.name, process.old_tau, cpu.end_time - time, queue))
                else:
                    print("time {}ms: Process {} started using the CPU for {}ms burst {}".format(time, process.name,
                          cpu.end_time - time, queue))
            queue.count_down = -1

        if time in io.queue:  # process finishes io burst
            for process in io.Pop(time):
                process.wait_start = time
                if is_sjf:
                    queue.Add(process, True)
                else:
                    queue.Add(process)
                if time < 10000:
                    if is_sjf:
                        print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue {}".format(time,
                              process.name, process.tau, queue))
                    else:
                        print("time {}ms: Process {} completed I/O; added to ready queue {}".format(time, process.name,
                                                                                                    queue))
                if queue.queue and not cpu.process and queue.count_down == -1:  # start context switch
                    queue.count_down = t_cs

        if not have_added and time in processes:  # process arrives
            for process in processes[time]:
                process.wait_start = time
                if is_sjf:
                    queue.Add(process, True)
                else:
                    queue.Add(process)
                if time < 10000:
                    if is_sjf:
                        print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(time,
                              process.name, process.tau, queue))
                    else:
                        print("time {}ms: Process {} arrived; added to ready queue {}".format(time, process.name,
                                                                                              queue))
        time += 1
    if is_sjf:
        print("time {}ms: Simulator ended for SJF {}".format(time - 1, queue))
    else:
        print("time {}ms: Simulator ended for FCFS {}".format(time - 1, queue))
    if is_sjf:
        simout("SJF", processes, time, num_context_switch, cpu_bound_context_switch, io_bound_context_switch)
    else:
        simout("FCFS", processes, time, num_context_switch, cpu_bound_context_switch, io_bound_context_switch)


def srt(processes, t_cs, total_process_num):
    print("time 0ms: Simulator started for SRT [Q <empty>]")
    queue, cpu, io, time, finish_num = setup(t_cs)
    num_context_switch, cpu_bound_context_switch, io_bound_context_switch = 0, 0, 0
    num_preemption, cpu_bound_preemption, io_bound_preemption = 0, 0, 0
    while finish_num < total_process_num:
        have_added = False
        if queue.length <= 0 and time in processes:  # process arrives
            have_added = True
            for process in processes[time]:
                process.wait_start = time
                queue.Add(process, True)
                if time < 10000:
                    print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(time,
                          process.name, process.tau, queue))

        if cpu.count_down != -1:  # preemption is occurring
            if cpu.count_down <= 0:  # preemption finished
                process = cpu.PopProcess()
                queue.Add(process, True)
                process.wait_start = time
                cpu.count_down = -1
                num_context_switch += 1
                if process.type == 0:
                    cpu_bound_context_switch += 1
                else:
                    io_bound_context_switch += 1
            else:
                cpu.count_down -= 1
        elif cpu.process:
            if cpu.end_time == time:  # process finishes cpu burst
                cpu.process.remain_tau = 0
                num_context_switch += 1
                if cpu.process.type == 0:
                    cpu_bound_context_switch += 1
                else:
                    io_bound_context_switch += 1
                if cpu.process.burst_num == 0:  # process finishes
                    print("time {}ms: Process {} terminated {}".format(time, cpu.process.name, queue))
                else:
                    if time < 10000:
                        print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} {} to go {}".format(time,
                              cpu.process.name, cpu.process.old_tau, cpu.process.burst_num,
                              'bursts' if cpu.process.burst_num > 1 else 'burst', queue))
                        print("time {}ms: Recalculating tau for process {}: old tau {}ms ==> new tau {}ms {}".format(
                            time, cpu.process.name, cpu.process.old_tau, cpu.process.tau, queue))
                        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms {}".format(
                            time, cpu.process.name, time + cpu.process.io_burst[0] + t_cs, queue))
            elif cpu.real_end_time == time:  # process finishes cpu burst and context switch
                process = cpu.PopProcess()
                if process.burst_num == 0:
                    finish_num += 1
                    process.turnaround_time = time - process.arrival_time - process.total_io_time
                else:
                    io.Add(process, time)

        if queue.queue and not cpu.process and queue.count_down == -1:  # no process in cpu, start context switch
            queue.count_down = t_cs
            queue.queue[0].total_wait_time += time - queue.queue[0].wait_start
            queue.queue[0].wait_start = time
        elif queue.count_down > 0:  # context switch is still going
            if queue.count_down == t_cs:
                cpu.next_process = queue.Pop()
            queue.count_down -= 1

        if queue.count_down == 0:  # context switch finishes, push process to cpu
            process = cpu.next_process
            cpu.next_process = None
            is_remain = cpu.AddProcess(process, time, True)
            if time < 10000:
                if is_remain and cpu.end_time - time < cpu.process.current_burst:
                    print("time {}ms: Process {} (tau {}ms) started using the CPU for remaining {}ms of "
                          "{}ms burst {}".format(time, process.name, process.old_tau, cpu.end_time - time,
                                                 cpu.process.current_burst, queue))
                else:
                    print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst {}".format(time,
                          process.name, process.old_tau, cpu.end_time - time, queue))
            queue.count_down = -1
            if cpu.process and queue.length > 0 and queue.queue[0].GetTau() < cpu.process.remain_tau:
                cpu.count_down = t_cs - 1
                num_preemption += 1
                queue.queue[0].total_wait_time += time - queue.queue[0].wait_start
                queue.queue[0].wait_start = time
                if cpu.process.type == 0:
                    cpu_bound_preemption += 1
                else:
                    io_bound_preemption += 1
                if time < 10000:
                    print("time {}ms: Process {} (tau {}ms) will preempt {} {}".format(time,
                        queue.queue[0].name, queue.queue[0].tau, cpu.process.name, queue))

        if time in io.queue:  # process finishes io burst
            for process in io.Pop(time):
                queue.Add(process, True)
                process.wait_start = time
                if cpu.process and process.tau < cpu.process.remain_tau and cpu.count_down == -1:
                    cpu.count_down = t_cs - 1
                    num_preemption += 1
                    if cpu.process.type == 0:
                        cpu_bound_preemption += 1
                    else:
                        io_bound_preemption += 1
                    if time < 10000:
                        print("time {}ms: Process {} (tau {}ms) completed I/O; preempting {} {}".format(time,
                              process.name, process.tau, cpu.process.name, queue))
                else:
                    if time < 10000:
                        print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue {}".format(time,
                              process.name, process.tau, queue))
                    if queue.queue and not cpu.process and queue.count_down == -1:  # start context switch
                        queue.count_down = t_cs
                        # queue.queue[0].total_wait_time += time - queue.queue[0].wait_start
                        queue.queue[0].wait_start = time

        if cpu.process and cpu.count_down == -1:  # process is running
            cpu.process.remain_tau -= 1
            cpu.process.remain_burst_time -= 1

        if not have_added and time in processes:  # process arrives
            for process in processes[time]:
                process.wait_start = time
                queue.Add(process, True)
                if time < 10000:
                    print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(time,
                          process.name, process.tau, queue))

        time += 1
    print("time {}ms: Simulator ended for SRT {}".format(time - 1, queue))
    simout("SRT", processes, time, num_context_switch, cpu_bound_context_switch,
           io_bound_context_switch, num_preemption, cpu_bound_preemption, io_bound_preemption)


def rr(processes, t_cs, total_process_num, t_slice):
    print("time 0ms: Simulator started for RR [Q <empty>]")
    queue, cpu, io, time, finish_num = setup(t_cs)
    num_context_switch, cpu_bound_context_switch, io_bound_context_switch = 0, 0, 0
    num_preemption, cpu_bound_preemption, io_bound_preemption = 0, 0, 0
    while finish_num < total_process_num:
        have_added = False
        if queue.length <= 0 and time in processes:  # process arrives
            have_added = True
            for process in processes[time]:
                process.wait_start = time
                queue.Add(process)
                if time < 10000:
                    print("time {}ms: Process {} arrived; added to ready queue {}".format(time, process.name,
                                                                                          queue))

        if cpu.count_down != -1:  # context switch: remove process from cpu
            if cpu.count_down <= 0:
                process = cpu.PopProcess()
                queue.Add(process)
                process.wait_start = time
                cpu.count_down = -1
                num_context_switch += 1
                num_preemption += 1
                if process.type == 0:
                    cpu_bound_context_switch += 1
                    cpu_bound_preemption += 1
                else:
                    io_bound_context_switch += 1
                    io_bound_preemption += 1
            else:
                cpu.count_down -= 1
        elif cpu.process:  # process is running
            cpu.process.remain_burst_time -= 1
            cpu.burst_time += 1
            if cpu.burst_time >= t_slice and time < cpu.end_time:  # time slice is up
                if queue.length <= 0:  # ready queue is empty
                    if time < 10000:
                        print("time {}ms: Time slice expired; no preemption because ready queue is empty [Q <empty>]"
                              .format(time))
                    cpu.burst_time = 0
                else:  # preemption
                    cpu.count_down = t_cs - 1
                    if time < 10000:
                        print("time {}ms: Time slice expired; preempting process {} with {}ms remaining {}".format(time,
                              cpu.process.name, cpu.process.remain_burst_time, queue))
            elif cpu.end_time == time:  # process finishes cpu burst
                num_context_switch += 1
                if cpu.process.type == 0:
                    cpu_bound_context_switch += 1
                else:
                    io_bound_context_switch += 1
                if cpu.process.burst_num == 0:  # process finishes
                    print("time {}ms: Process {} terminated {}".format(time, cpu.process.name, queue))
                else:
                    if time < 10000:
                        print("time {}ms: Process {} completed a CPU burst; {} {} to go {}".format(time,
                              cpu.process.name, cpu.process.burst_num, "bursts" if cpu.process.burst_num > 1
                                                                                                   else "burst", queue))
                        print("time {}ms: Process {} switching out of CPU; blocking on I/O until time {}ms {}".format(
                              time, cpu.process.name, time + cpu.process.io_burst[0] + t_cs, queue))
            elif cpu.real_end_time == time:  # process finishes cpu burst and context switch
                process = cpu.PopProcess()
                if process.burst_num == 0:
                    finish_num += 1
                    process.turnaround_time = time - process.arrival_time - process.total_io_time
                else:
                    io.Add(process, time)

        if queue.queue and not cpu.process and queue.count_down == -1:  # context switch: add process to cpu
            queue.count_down = t_cs
            queue.queue[0].total_wait_time += time - queue.queue[0].wait_start
            queue.queue[0].wait_start = 0
        elif queue.count_down > 0:  # context switch is still going
            if queue.count_down == t_cs:
                cpu.next_process = queue.Pop()
            queue.count_down -= 1

        if queue.count_down == 0:  # context switch finishes, push process to cpu
            process = cpu.next_process
            cpu.next_process = None
            is_remain = cpu.RR_AddProcess(process, time)
            if time < 10000:
                if is_remain and cpu.end_time - time < cpu.process.current_burst:
                    print("time {}ms: Process {} started using the CPU for remaining {}ms of {}ms burst {}".format(
                        time, process.name, cpu.end_time - time, process.current_burst, queue))
                else:
                    print("time {}ms: Process {} started using the CPU for {}ms burst {}".format(time, process.name,
                                                                                            cpu.end_time - time, queue))
            queue.count_down = -1

        if time in io.queue:  # process finishes io burst
            for process in io.Pop(time):
                queue.Add(process)
                process.wait_start = time
                if time < 10000:
                    print("time {}ms: Process {} completed I/O; added to ready queue {}".format(time, process.name,
                                                                                                queue))
                if queue.queue and not cpu.process and queue.count_down == -1:  # start context switch
                    queue.count_down = t_cs

        if not have_added and time in processes:  # process arrives
            for process in processes[time]:
                queue.Add(process)
                process.wait_start = time
                if time < 10000:
                    print("time {}ms: Process {} arrived; added to ready queue {}".format(time, process.name,
                                                                                              queue))
        time += 1
    print("time {}ms: Simulator ended for RR {}".format(time - 1, queue))
    simout("RR", processes, time, num_context_switch, cpu_bound_context_switch,
           io_bound_context_switch, num_preemption, cpu_bound_preemption, io_bound_preemption)


if __name__ == "__main__":
    # get argv1 to argv5 from command line
    try:
        num_process = int(sys.argv[1])
        num_cpu = int(sys.argv[2])
        num_io = num_process - num_cpu
        seed = int(sys.argv[3])
        lambda_ = float(sys.argv[4])
        upper_limit = int(sys.argv[5])
        t_cs = int(sys.argv[6])
        alpha = float(sys.argv[7])
        t_slice = int(sys.argv[8])
    except (IndexError, ValueError):
        print("ERROR: Invalid arguments")
        sys.exit(1)
    if num_process < 0 or num_process > 26 or num_cpu < 0 or alpha < 0:
        print("ERROR: Invalid number of processes or alpha")
        sys.exit(1)
    if t_cs % 2 != 0 or t_cs <= 0:
        print("ERROR: Invalid context switch time")
        sys.exit(1)
    if num_cpu > num_process:
        print("ERROR: More CPUs than processes")
        sys.exit(1)
    if alpha > 1:
        print("ERROR: Invalid alpha value")
        sys.exit(1)
    if lambda_ <= 0 or upper_limit <= 0 or t_slice <= 0:
        print("ERROR: Invalid arguments")
        sys.exit(1)
    print("<<< PROJECT PART I -- process set (n={}) with {} CPU-bound {} >>>".format(
        num_process, num_cpu, "process" if num_cpu == 1 else "processes"))
    # create drand48 object
    rand = Rand48(seed, lambda_, upper_limit)
    processes = {}
    for i in range(num_process):
        process = Process(rand.floor(), rand.num_cpu(), i, lambda_, alpha)
        if i > num_io - 1:
            process.SetTypeCPU()
        print("{} process {}: arrival time {}ms; {} CPU bursts".format(
              process.type_str, process.name, process.arrival_time, process.num_burst))
        for j in range(process.num_burst):
            cpu_time = rand.ceil()
            if process.type == 0:  # cpu-bound process
                cpu_time *= 4
            process.AddCPUBurst(cpu_time)
            if j != process.num_burst - 1:
                io_time = rand.ceil() * 10
                if process.type == 0:  # cpu-bound process
                    io_time //= 8
                process.AddIOBurst(io_time)
        if process.arrival_time in processes:
            processes[process.arrival_time].append(process)
        else:
            processes[process.arrival_time] = [process]
    print()
    print("<<< PROJECT PART II -- t_cs={}ms; alpha={:.2f}; t_slice={}ms >>>".format(t_cs, alpha, t_slice))
    f = open("simout.txt", "w")
    f.write("")
    f.close()
    temp = copy.deepcopy(processes)
    fcfs_sjf(temp, t_cs // 2, num_process)
    print()
    temp = copy.deepcopy(processes)
    fcfs_sjf(temp, t_cs // 2, num_process, True)
    print()
    temp = copy.deepcopy(processes)
    srt(temp, t_cs // 2, num_process)
    print()
    temp = copy.deepcopy(processes)
    rr(temp, t_cs // 2, num_process, t_slice)
