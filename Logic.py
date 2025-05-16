import numpy as np
import matplotlib as plt
from matplotlib.figure import Figure
colormap = plt.colormaps['tab10']

class Scheduler:
    def __init__(self, processes):
        self.processes = processes
        self.num_processes = len(processes)
        self.turnaround_times = [0] * self.num_processes
        self.waiting_times = [0] * self.num_processes
        self.completion_times = [0] * self.num_processes
        self.current_time = 0
        self.completed = [False] * self.num_processes
        self.gantt_chart = []

    def run(self):
        pass
    
    def visualize(self):
        fig, ax = self.create_plot('Scheduling Visualization')
        pid_to_y = {pid: i for i, pid in enumerate(sorted(set(pid for start, end, pid, color in self.gantt_chart)))}
        
        for start, end, pid, color in self.gantt_chart:
            y_position = pid_to_y[pid]
            ax.broken_barh([(start, end - start)], (y_position, 1), facecolors=color)
            
            text_x = start + (end - start) / 2
            text_y = y_position + 0.5
            ax.text(text_x, text_y, 'P' + str(pid), ha='center', va='center', color='white', fontsize=10)
        
        ax.set_yticks([])
        self.finish_plot(ax)
        return fig

    def create_plot(self, title):
        fig = Figure(figsize=(20, 6))
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time')
        ax.set_ylabel('Process')
        ax.set_title(title)
        return fig, ax

    def finish_plot(self, ax):
        ax.set_xticks(np.arange(0, max(self.completion_times, default=0) + 1, 1))
        ax.grid(True, which='both', axis='x', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
            
class FCFS(Scheduler):
    def run(self):
        self.processes.sort(key=lambda x: x["arrival_time"])

        for i, process in enumerate(self.processes):
            if i == 0:
                self.waiting_times[i] = 0
                self.current_time = process["arrival_time"]
            else:
                if self.current_time < process["arrival_time"]:
                    self.current_time = process["arrival_time"]

                self.waiting_times[i] = self.current_time - process["arrival_time"]

            start_time = self.current_time
            self.current_time += process["burst_time"]
            self.completion_times[i] = self.current_time
            self.turnaround_times[i] = self.completion_times[i] - process["arrival_time"]
            self.gantt_chart.append((start_time, self.current_time, process['process_id'], colormap(i / self.num_processes)))

class Priority(Scheduler):
    def run(self):
        self.processes.sort(key=lambda x: (x["priority"], x["arrival_time"]))
        
        while any(not self.completed[i] for i in range(self.num_processes)):
            next_process = next((i for i in range(self.num_processes) if not self.completed[i] and self.processes[i]["arrival_time"] <= self.current_time), -1)
            
            if next_process == -1:
                min_arrival_time = min((proc["arrival_time"] for i, proc in enumerate(self.processes) if not self.completed[i]), default=self.current_time)
                self.current_time = min_arrival_time
                continue
            
            next_process = min((i for i in range(self.num_processes) if not self.completed[i] and self.processes[i]["arrival_time"] <= self.current_time), key=lambda i: self.processes[i]["priority"])
            start_time = self.current_time
            
            self.current_time += self.processes[next_process]["burst_time"]
            self.completion_times[next_process] = self.current_time
            self.completed[next_process] = True
            self.turnaround_times[next_process] = self.current_time - self.processes[next_process]["arrival_time"]
            self.waiting_times[next_process] = self.turnaround_times[next_process] - self.processes[next_process]["burst_time"]
            self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / self.num_processes)))
                    
class Priority_pre(Scheduler):
    
    def run(self):
        self.processes.sort(key=lambda x: (x["priority"], x["arrival_time"]))
        remaining_burst_times = {i: proc["burst_time"] for i, proc in enumerate(self.processes)}
        
        while any(not self.completed[i] for i in range(self.num_processes)):
            current_process = None
            for i in range(self.num_processes):
                if not self.completed[i] and self.processes[i]["arrival_time"] <= self.current_time:
                    if current_process is None or self.processes[i]["priority"] < self.processes[current_process]["priority"]:
                        current_process = i

            if current_process is None:
                self.current_time = min(proc["arrival_time"] for i, proc in enumerate(self.processes) if not self.completed[i])
                continue

            start_time = self.current_time
            next_arrival_time = min((proc["arrival_time"] for i, proc in enumerate(self.processes) if proc["arrival_time"] > self.current_time and not self.completed[i]), default=float('inf'))
            execution_time = min(remaining_burst_times[current_process], next_arrival_time - self.current_time)

            self.current_time += execution_time
            remaining_burst_times[current_process] -= execution_time

            if remaining_burst_times[current_process] == 0:
                self.completed[current_process] = True
                self.completion_times[current_process] = self.current_time
                self.turnaround_times[current_process] = self.current_time - self.processes[current_process]["arrival_time"]
                wait = self.turnaround_times[current_process] - self.processes[current_process]["burst_time"]
                self.waiting_times[current_process] = max(wait, 0)

            color = colormap(current_process / self.num_processes)
            self.gantt_chart.append((start_time, self.current_time, self.processes[current_process]['process_id'], color))
            
class HRRN(Scheduler):
    def run(self):
        num_processes = len(self.processes)
        remaining_burst_time = [p["burst_time"] for p in self.processes]
        arrival_time = [p["arrival_time"] for p in self.processes]
        completed = [False] * num_processes

        while any(not comp for comp in completed):
            next_process = -1
            max_response_ratio = -1

            for i in range(num_processes):
                if not completed[i] and arrival_time[i] <= self.current_time:
                    response_time = (self.current_time - arrival_time[i] + remaining_burst_time[i])
                    response_ratio = response_time / remaining_burst_time[i]
                    
                    if response_ratio > max_response_ratio:
                        max_response_ratio = response_ratio
                        next_process = i

            if next_process == -1:
                next_times = [arrival_time[i] for i in range(num_processes) if not completed[i]]
                self.current_time = min(next_times)
            else:
                self.waiting_times[next_process] = self.current_time - arrival_time[next_process]
                start_time = self.current_time
                self.current_time += remaining_burst_time[next_process]
                self.turnaround_times[next_process] = self.current_time - arrival_time[next_process]
                self.completion_times[next_process] = self.current_time
                completed[next_process] = True
                self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / num_processes)))

class LJF(Scheduler):
    def run(self):
        self.processes.sort(key=lambda x: x["burst_time"], reverse=True)
        completed = [False] * self.num_processes

        while any(not comp for comp in completed):
            next_process = -1

            for i in range(self.num_processes):
                if not completed[i] and self.processes[i]["arrival_time"] <= self.current_time:
                    next_process = i
                    break

            if next_process == -1:
                future_arrivals = [p["arrival_time"] for i, p in enumerate(self.processes) if not completed[i]]
                self.current_time = min(future_arrivals)
                continue

            start_time = self.current_time
            self.current_time += self.processes[next_process]["burst_time"]
            self.completion_times[next_process] = self.current_time
            completed[next_process] = True

            self.turnaround_times[next_process] = self.current_time - self.processes[next_process]["arrival_time"]
            self.waiting_times[next_process] = self.turnaround_times[next_process] - self.processes[next_process]["burst_time"]
            self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / self.num_processes)))

class SJF(Scheduler):
    def run(self):
        self.processes.sort(key=lambda x: x["burst_time"])
        completed = [False] * self.num_processes

        while any(not comp for comp in completed):
            next_process = -1
            min_burst_time = float('inf')

            for i in range(self.num_processes):
                if not completed[i] and self.processes[i]["arrival_time"] <= self.current_time and self.processes[i]["burst_time"] < min_burst_time:
                    next_process = i
                    min_burst_time = self.processes[i]["burst_time"]

            if next_process == -1:
                future_arrivals = [p["arrival_time"] for i, p in enumerate(self.processes) if not completed[i]]
                self.current_time = min(future_arrivals)
            else:
                start_time = self.current_time
                self.current_time += self.processes[next_process]["burst_time"]
                self.completion_times[next_process] = self.current_time
                completed[next_process] = True

                self.turnaround_times[next_process] = self.current_time - self.processes[next_process]["arrival_time"]
                self.waiting_times[next_process] = self.turnaround_times[next_process] - self.processes[next_process]["burst_time"]
                self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / self.num_processes)))
                
class LRTF(Scheduler):
    def run(self):
        num_processes = len(self.processes)
        remaining_burst_time = [p["burst_time"] for p in self.processes]
        completed = [False] * num_processes

        while any(not comp for comp in completed):
            next_process = -1
            max_remaining_time = 0

            for i in range(num_processes):
                if not completed[i] and remaining_burst_time[i] > 0 and self.processes[i]["arrival_time"] <= self.current_time:
                    if remaining_burst_time[i] > max_remaining_time:
                        next_process = i
                        max_remaining_time = remaining_burst_time[i]

            if next_process == -1:
                next_times = [p["arrival_time"] for i, p in enumerate(self.processes) if not completed[i] and p["arrival_time"] > self.current_time]
                self.current_time = min(next_times) if next_times else self.current_time + 1
            else:
                start_time = self.current_time
                self.current_time += 1
                remaining_burst_time[next_process] -= 1

                for i in range(num_processes):
                    if i != next_process and not completed[i] and self.processes[i]["arrival_time"] <= self.current_time - 1:
                        self.waiting_times[i] += 1

                self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / num_processes)))

                if remaining_burst_time[next_process] == 0:
                    self.completion_times[next_process] = self.current_time
                    completed[next_process] = True
                    self.turnaround_times[next_process] = self.current_time - self.processes[next_process]["arrival_time"]
                    
class SRTF(Scheduler):
    def run(self):
        num_processes = len(self.processes)
        remaining_burst_time = [p["burst_time"] for p in self.processes]
        completed = [False] * num_processes

        while any(not comp for comp in completed):
            next_process = -1
            min_remaining_time = float('inf')

            for i in range(num_processes):
                if not completed[i] and remaining_burst_time[i] > 0 and self.processes[i]["arrival_time"] <= self.current_time and remaining_burst_time[i] < min_remaining_time:
                    next_process = i
                    min_remaining_time = remaining_burst_time[i]

            if next_process == -1:
                future_arrivals = [p["arrival_time"] for i, p in enumerate(self.processes) if not completed[i]]
                self.current_time = min(future_arrivals)
            else:
                start_time = self.current_time
                self.current_time += 1
                remaining_burst_time[next_process] -= 1

                for i in range(num_processes):
                    if i != next_process and not completed[i] and self.processes[i]["arrival_time"] <= self.current_time - 1:
                        self.waiting_times[i] += 1
                
                self.gantt_chart.append((start_time, self.current_time, self.processes[next_process]['process_id'], colormap(next_process / num_processes)))
                        
                if remaining_burst_time[next_process] == 0:
                    self.completion_times[next_process] = self.current_time
                    completed[next_process] = True
                    self.turnaround_times[next_process] = self.current_time - self.processes[next_process]["arrival_time"]
     