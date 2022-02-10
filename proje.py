import numpy as np
import random
import pandas as pd
import math
import matplotlib.pyplot as plt

class Process:
    def __init__(self,name,arrival_time,burst_time,priority=0):
        self.name=name
        self.arrival_time=arrival_time
        self.burst_time=burst_time
        self.priority=priority
        self.remaining_time=burst_time
        self.start_time=0
        self.end_time=0
        self.waiting_time=0
        self.turnaround_time=0
        self.is_completed=False
        self.is_started = False
    
    def complete(self,t):
        self.end_time=t
        self.turnaround_time=self.end_time-self.arrival_time
        self.waiting_time=self.turnaround_time-self.burst_time
        self.is_completed=True
    
class Queue:
    def __init__(self,MLFQ,max_burst_time,priority):
        self.max_burst_time = max_burst_time
        self.priority = priority
        self.processes = []
        self.next_queue = None        
        self.last_queue = None
        self.is_completed = True
        self.MLFQ = MLFQ
        self.last = False

    def add_process(self,process):
        self.processes.append(process)
        self.is_completed = False

    def remove_process(self):
        self.processes.pop(0)
        if len(self.processes) == 0:
            self.is_completed = True
        
    def get_process(self):
        return self.processes[0]

    def complete_process(self):
        process = self.get_process()
        process.complete(self.MLFQ.time)
        self.remove_process()       


class MLFQ:                         #Multilevel Feedback Queue Scheduling
    def __init__(self,queues,processes):
        self.init_processes(processes)
        self.init_queues(queues)
        self.time = 0
        self.complete_processes = []
        self.n = len(self.processes)

        

    def init_queues(self,queues):
        self.queues = []
        for q in queues:
            self.add_queue(Queue(self,q,0))

    def add_queue(self,queue):
        if len(self.queues) == 0:
            self.queues.append(queue)
            self.queues[0].last = True
        else:
            self.queues.append(queue)
            self.queues[-1].last = True
            self.queues[-2].last = False
            self.queues[-2].next_queue = queue

    def init_processes(self,processes):
        self.processes = []
        for p in range(len(processes)):
            process = Process(p, processes[p][0],processes[p][1],0)
            self.processes.append(process)

    def check_processes(self):
        if len(self.processes) > 0:
            if self.time >= self.processes[0].arrival_time:
                self.queues[0].add_process(self.processes[0])
                self.processes.pop(0)

    def get_highest_priority_queue(self):
        for queue in self.queues:
            if len(queue.processes) > 0:
                return queue
                
        return None

    def run(self):
        self.current_queue = self.queues[0]
        self.current_process = None
        self.cpu_state = 'free'
        while len(self.complete_processes) != self.n:
            print('complete processes: ',len(self.complete_processes))
            print("Time: ",self.time)
            
            self.check_processes()
            self.current_queue = self.get_highest_priority_queue()
            if self.current_queue is not None:
                self.cpu_state = 'busy'
                turn_time = 0
                if self.current_queue.last:
                    self.current_process = self.current_queue.get_process()
                    while self.current_process.remaining_time != 0:
                        self.current_process.remaining_time -= 1
                        self.time += 1
                    self.current_queue.complete_process()
                    self.complete_processes.append(self.current_process)
                    
                else:
                    self.current_process = self.current_queue.get_process()
                    while turn_time < self.current_queue.max_burst_time:
                        if not self.current_process.is_started:
                            self.current_process.start_time = self.time
                            self.current_process.is_started = True

                        self.current_process.remaining_time -= 1
                        self.time += 1
                        if self.current_process.remaining_time == 0:
                            self.current_queue.complete_process()
                            self.complete_processes.append(self.current_process)
                            self.cpu_state = 'free'
                            break
                        
                        turn_time += 1
                    if not self.current_process.is_completed:
                        self.current_queue.next_queue.add_process(self.current_process)
                        self.current_queue.remove_process()
            else:
                self.time += 1

    def record(self):
        pass


def generate_process(start,end,number_of_processes,max_burst_time):    
    arrival_times = np.random.randint(start,end,number_of_processes)
    burst_times = np.random.randint(1,max_burst_time,number_of_processes)
    arrival_times = np.sort(arrival_times)
    process =  np.array(list((zip(arrival_times,burst_times)))).reshape(number_of_processes,2)
    return process
    


def main(processes,start,end,number_of_processes,max_burst_time):
    # process = generate_process(start,end,number_of_processes,max_burst_time)
    mlfq = MLFQ([4,8,16],processes)
    mlfq.run()
    # mlfq.print_process()