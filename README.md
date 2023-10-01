# CPU_Scheduling_Simulator

 ## Introduction
### Purpose
This project aims to simulate an operating system with a set of processes defined as programs in execution. A process, depending on its current state will reside in either CPU, ready queue, or I/O subsystem. The simulation will use 4 algorithms: FCFS(First-Come-First-Served), SJF(Shortest Job First), SRT(Shortest Remaining Time), RR(Round Robin). More than that, data will be collected during the simulation process to calculate relative statistics. 

### Process States
A process will have three states:
* RUNNING: The process actively using the CPU and executing instructions
* READY: The process is ready to execute a CPU burst. It will reside in the ready queue, which will order processes based on the algorithm that the simulation used
* WAITING: blocked on I/O or some other event. 

Other than that, a process will be given a number, which represents the number of CPU bursts it requires to finish.

Each process will be classified as either CPU-bound or I/O-bound. 

## Simulation Workflow
1. A process arrives in the waiting queue based on its arrival time.
2. If there is no process using the CPU, the process will get into the CPU and start a new CPU burst.
3. After the CPU burst, the process will get into the I/O subsystem, waiting for an operation by a user.
4. After the WAITING state, the process will be back in the queue and waiting for a new CPU burst. Depending on the simulation algorithm, a process might preempt other processes. 

## Simulation Algorithms
* **FCFS**: The FCFS algorithm is a non-preemptive algorithm in which processes simply line up in the ready queue, waiting to use the CPU.
* **SJF**: In SJF, processes are stored in the ready queue in order of priority based on their anticipated CPU burst times. More specifically, the process with the shortest predicted CPU burst time will be selected as the next process executed by the CPU.
* **SRT**: The SRT algorithm is a preemptive version of the SJF algorithm. In SRT, when a process arrives, if it has a predicted CPU burst time that is less than the remaining predicted time of the currently running process, a preemption occurs. When such a preemption occurs, the currently running process is simply added to the ready queue. 
* **RR**: The RR algorithm is essentially the FCFS algorithm with time slice `t_slice`. Each process is given `t_slice` amount of time to complete its CPU burst. If the time slice expires, the process is preempted and added to the end of the ready queue.

## Drand48
In this project, drand48, a pseudo-random algorithm, is used to generate time collections for processes for their CPU burst times and I/O burst times.

## Input Argument
* **n**: The number of processes to simulate.
* **n_cpu**: the number of CPU-bound processes.
* **seed**: A pseudo-random number generator to determine the interarrival times of CPU bursts.
* **lambda**: An exponential distribution, which is used to determine interarrival times.
* **upper_limit**: The upper bound for valid pseudo-random numbers.
* **t_cs**: The time, in milliseconds, that it takes to perform a context switch. Specifically, the first half of the context switch time is the time required to remove the given process from the CPU; the second half of the context switch time is the time required to bring the next process in to use the CPU. 
* **alpha**: For the SJF and SRT algorithms, since we cannot know the actual CPU burst times beforehand, we will rely on estimates determined via exponential averaging.
* **t_slice**: For the RR algorithm, define the time slice value, t_slice, measured in milliseconds.

## Statistics
The following factors will be calculated and outputted into simout.txt:
* CPU utilization
* average wait time
* average turnaround time
* number of context switches
* number of preemptions

## Input Example

```
bash$ python3 project.py 3 1 1024 0.001 3000 4 0.75 256
```