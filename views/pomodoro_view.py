import tkinter as tk
from tkinter import ttk
import time
import threading

class PomodoroView:
    def __init__(self, parent):
        self.parent = parent
        self.is_running = False
        self.work_time = 25 * 60  # 工作时长25分钟
        self.break_time = 5 * 60  # 休息时长5分钟
        self.timer = None
        self.time_left = self.work_time

        self.create_widgets()

    def create_widgets(self):
        # 创建Style对象用于自定义样式
        style = ttk.Style()
        style.configure("TLabel", background="#f5f5f5", foreground="black", font=("Microsoft YaHei", 12))
        style.configure("TButton", padding=6, relief="flat", font=("Microsoft YaHei", 10), background="green", foreground="white")
        style.map("TButton", background=[("active", "#45a049")])  # 激活时的颜色

        # 标题标签
        title_label = ttk.Label(self.parent, text="番茄钟", font=("Microsoft YaHei", 24, "bold"))
        title_label.pack(pady=20)

        # 显示时间的标签
        self.time_label = ttk.Label(self.parent, text=self.format_time(self.work_time), font=("Microsoft YaHei", 36, "bold"), foreground="green")
        self.time_label.pack(pady=20)

        # 按钮框架用于居中对齐
        button_frame = tk.Frame(self.parent)  # 使用 tk.Frame 而不是 ttk.Frame，这样可以避免背景设置问题
        button_frame.pack(pady=20)

        # 开始按钮
        start_button = ttk.Button(button_frame, text="开始", command=self.start_timer)
        start_button.grid(row=0, column=0, padx=10)

        # 重置按钮
        reset_button = ttk.Button(button_frame, text="重置", command=self.reset_timer)
        reset_button.grid(row=0, column=1, padx=10)

        # 暂停按钮
        pause_button = ttk.Button(button_frame, text="暂停", command=self.pause_timer)
        pause_button.grid(row=0, column=2, padx=10)

        # 状态标签（用于显示工作中/休息中）
        self.status_label = ttk.Label(self.parent, text="", font=("Microsoft YaHei", 14))
        self.status_label.pack(pady=10)

    def format_time(self, seconds):
        """格式化秒为 MM:SS"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def start_timer(self):
        """开始倒计时"""
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="工作中...", foreground="green")
            self.countdown(self.time_left)

    def pause_timer(self):
        """暂停倒计时"""
        if self.is_running:
            self.is_running = False
            if self.timer is not None:
                self.parent.after_cancel(self.timer)
                self.status_label.config(text="暂停中", foreground="orange")

    def reset_timer(self):
        """重置倒计时"""
        self.is_running = False
        if self.timer is not None:
            self.parent.after_cancel(self.timer)
        self.time_left = self.work_time
        self.time_label.config(text=self.format_time(self.time_left), foreground="green")
        self.status_label.config(text="已重置", foreground="blue")

    def countdown(self, remaining_time):
        """倒计时逻辑"""
        if remaining_time >= 0 and self.is_running:
            self.time_left = remaining_time
            self.time_label.config(text=self.format_time(remaining_time))
            self.timer = self.parent.after(1000, self.countdown, remaining_time - 1)
        elif remaining_time < 0 and self.is_running:
            self.is_running = False
            self.status_label.config(text="休息中...", foreground="blue")
            self.time_left = self.break_time
            self.countdown(self.break_time)
