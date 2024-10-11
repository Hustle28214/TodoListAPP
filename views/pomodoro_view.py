# views/pomodoro_view.py

import tkinter as tk
import time
import threading

class PomodoroView:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.is_running = False
        self.work_time = 25 * 60  # 默认工作时间 25 分钟
        self.break_time = 5 * 60  # 默认休息时间 5 分钟

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self.frame, text="番茄钟", font=("Arial", 16))
        label.pack(pady=10)

        self.time_label = tk.Label(self.frame, text="25:00", font=("Arial", 48))
        self.time_label.pack(pady=10)

        # 设置工作时间和休息时间
        tk.Label(self.frame, text="设置工作时间（分钟）").pack()
        self.work_time_entry = tk.Entry(self.frame)
        self.work_time_entry.insert(0, "25")
        self.work_time_entry.pack()

        tk.Label(self.frame, text="设置休息时间（分钟）").pack()
        self.break_time_entry = tk.Entry(self.frame)
        self.break_time_entry.insert(0, "5")
        self.break_time_entry.pack()

        # 开始、暂停、重置按钮
        start_button = tk.Button(self.frame, text="开始", command=self.start_timer)
        start_button.pack(side=tk.LEFT, padx=10)

        pause_button = tk.Button(self.frame, text="暂停", command=self.pause_timer)
        pause_button.pack(side=tk.LEFT, padx=10)

        reset_button = tk.Button(self.frame, text="重置", command=self.reset_timer)
        reset_button.pack(side=tk.LEFT, padx=10)

    def start_timer(self):
        if not self.is_running:
            self.work_time = int(self.work_time_entry.get()) * 60
            self.break_time = int(self.break_time_entry.get()) * 60
            self.is_running = True
            self.current_time = self.work_time
            self.run_timer()

    def run_timer(self):
        def update_time():
            while self.is_running and self.current_time > 0:
                mins, secs = divmod(self.current_time, 60)
                time_format = f"{mins:02d}:{secs:02d}"
                self.time_label.config(text=time_format)
                self.current_time -= 1
                time.sleep(1)
            if self.current_time == 0 and self.is_running:
                self.switch_mode()

        self.timer_thread = threading.Thread(target=update_time)
        self.timer_thread.start()

    def switch_mode(self):
        if self.current_time == 0 and self.is_running:
            if self.time_label.cget("text") == "00:00":
                self.current_time = self.break_time
                self.time_label.config(text="休息时间！")
                self.run_timer()
            elif self.time_label.cget("text") == "休息时间！":
                self.reset_timer()

    def pause_timer(self):
        self.is_running = False

    def reset_timer(self):
        self.is_running = False
        self.current_time = self.work_time
        self.time_label.config(text="25:00")

