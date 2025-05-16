from Logic import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton,
    QComboBox, QHBoxLayout, QHeaderView, QTableWidget,
    QTableWidgetItem, QLabel, QWidget, QMessageBox
)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Process Scheduling Simulator'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(10, 40, 1800, 800)
        
        widget = QWidget(self)
        self.setCentralWidget(widget)
        
        main_layout = QVBoxLayout(widget)
        top_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        
        main_layout.addLayout(top_layout)
        top_layout.addLayout(left_layout, 1)
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FCFS", "Priority", "Priority (Preemitive)", "LJF", "SJF", "LRTF", "SRTF", "HRRN"])
        self.algorithm_combo.currentTextChanged.connect(self.adjust_columns)
        
        left_layout.addWidget(QLabel("Select Algorithm:"))
        left_layout.addWidget(self.algorithm_combo)
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(2)
        self.process_table.setHorizontalHeaderLabels(["Arrival Time", "Burst Time"])
        left_layout.addWidget(self.process_table)
        
        button_layout = QHBoxLayout()
        
        add_row_button = QPushButton('Add Process')
        add_row_button.clicked.connect(self.add_process)
        button_layout.addWidget(add_row_button)
        
        delete_row_button = QPushButton('Delete Process')
        delete_row_button.clicked.connect(self.delete_process)
        button_layout.addWidget(delete_row_button)
        
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear_processes)
        button_layout.addWidget(clear_button)
        
        left_layout.addLayout(button_layout)
        
        self.run_button = QPushButton('Run', self)
        self.run_button.clicked.connect(self.run_algorithm)
        left_layout.addWidget(self.run_button)
        
        right_layout = QVBoxLayout()
        top_layout.addLayout(right_layout, 2)
        
        self.figure = Figure(figsize=(20, 6))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)
        
        bottom_layout = QVBoxLayout()
        main_layout.addLayout(bottom_layout)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Process", "Arrival Time", "Burst Time", "Turnaround Time", "Waiting Time", "Completion Time"])        
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        bottom_layout.addWidget(self.results_table)

    def adjust_columns(self):
        if self.algorithm_combo.currentText() == "Priority" or self.algorithm_combo.currentText() == "Priority (Preemitive)":
            self.process_table.setColumnCount(3)
            self.process_table.setHorizontalHeaderLabels(["Arrival Time", "Burst Time", "Priority"])
        else:
            self.process_table.setColumnCount(2)
            self.process_table.setHorizontalHeaderLabels(["Arrival Time", "Burst Time"])

    def add_process(self):
        row_count = self.process_table.rowCount()
        self.process_table.insertRow(row_count)
        for i in range(self.process_table.columnCount()):
            self.process_table.setItem(row_count, i, QTableWidgetItem(""))

    def delete_process(self):
        indices = self.process_table.selectionModel().selectedRows()
        for index in sorted(indices, reverse=True):
            self.process_table.removeRow(index.row())

    def run_algorithm(self):
        algorithm = self.algorithm_combo.currentText()
        processes = []
        
        for i in range(self.process_table.rowCount()):
            arrival_time_item = self.process_table.item(i, 0)
            burst_time_item = self.process_table.item(i, 1)

            if not (arrival_time_item and arrival_time_item.text().strip() and
                    burst_time_item and burst_time_item.text().strip()):
                self.show_error_message("Please fill in all the fields.")
                return
            try:
                arrival_time = float(arrival_time_item.text())
                burst_time = float(burst_time_item.text())
                
                if arrival_time < 0 or burst_time < 0:
                    raise ValueError("Arrival time and burst time must be non-negative.")
            except ValueError as e:
                self.show_error_message(f"Please enter valid numbers for arrival time and burst time: {e}")
                return
              
            if algorithm == "Priority" or algorithm == "Priority (Preemitive)":
                priority_item = self.process_table.item(i, 2)
                    
                if priority_item is None or not priority_item.text().strip():
                    self.show_error_message("Please fill in all the fields.")
                    return
                try:
                    priority = float(priority_item.text())
                    
                    if priority <= 0:
                        raise ValueError("Priority must be greater than zero.")
                except ValueError as e:
                    self.show_error_message(f"Please enter valid numbers for priority: {e}")
                    return
                
                processes.append({"process_id": i + 1, "arrival_time": arrival_time, "burst_time": burst_time, "priority": priority})
            else:
                processes.append({"process_id": i + 1, "arrival_time": arrival_time, "burst_time": burst_time})
                            
        if not processes:
            self.show_error_message("Please add at least one process.")
            return
        
        if algorithm == "FCFS":
            scheduler = FCFS(processes)
        elif algorithm == "Priority":
            scheduler = Priority(processes)
        elif algorithm == "Priority (Preemitive)":
            scheduler = Priority_pre(processes)
        elif algorithm == "LJF":
            scheduler = LJF(processes)
        elif algorithm == "SJF":
            scheduler = SJF(processes)
        elif algorithm == "LRTF":
            scheduler = LRTF(processes)
        elif algorithm == "SRTF":
            scheduler = SRTF(processes)
        elif algorithm == "HRRN":
            scheduler = HRRN(processes)
        
        scheduler.run()
        self.visualize(scheduler)
        self.table(scheduler)
        
    def visualize(self, scheduler):
        self.figure.clear()
        fig = scheduler.visualize()
        self.canvas.figure = fig
        self.canvas.draw()
        self.canvas.figure.tight_layout()

    def table(self, scheduler):
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        
        self.results_table.setRowCount(len(scheduler.processes) + 1)
        header_labels = ["Process", "Arrival Time", "Burst Time", "Turnaround Time", "Waiting Time", "Completion Time"]
            
        if isinstance(scheduler, Priority) or isinstance(scheduler, Priority_pre):
            header_labels.insert(3, "Priority")
            self.results_table.setColumnCount(7)
                
        self.results_table.setHorizontalHeaderLabels(header_labels)
            
        for i, process in enumerate(scheduler.processes):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(process['process_id'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(process['arrival_time'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(process['burst_time'])))
            
            if isinstance(scheduler, Priority) or isinstance(scheduler, Priority_pre):
                self.results_table.setItem(i, 3, QTableWidgetItem(str(process['priority'])))
                col_offset = 1
            else:
                col_offset = 0
            
            self.results_table.setItem(i, 3 + col_offset, QTableWidgetItem(str(scheduler.turnaround_times[i])))
            self.results_table.setItem(i, 4 + col_offset, QTableWidgetItem(str(scheduler.waiting_times[i])))
            self.results_table.setItem(i, 5 + col_offset, QTableWidgetItem(str(scheduler.completion_times[i])))
            
        avg_turnaround = sum(scheduler.turnaround_times) / len(scheduler.processes)
        avg_waiting = sum(scheduler.waiting_times) / len(scheduler.processes)
            
        self.results_table.setItem(len(scheduler.processes), 0, QTableWidgetItem("Average:"))
        self.results_table.setItem(len(scheduler.processes), 4 + col_offset, QTableWidgetItem(str(avg_waiting)))
        self.results_table.setItem(len(scheduler.processes), 3 + col_offset, QTableWidgetItem(str(avg_turnaround)))

    def clear_processes(self):
        self.process_table.clearContents()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()