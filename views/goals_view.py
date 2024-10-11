# views/goals_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar  # 导入 Calendar 控件
from datetime import datetime

class GoalsView:
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.goals = []  # 保存用户的目标
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self.frame, text="目标设置", font=("Microsoft YaHei", 16))
        label.pack(pady=10)

        # 目标输入框
        self.goal_entry = tk.Entry(self.frame, width=50)
        self.goal_entry.pack(pady=5)

        # 目标时间选择器（替换为日历控件）
        self.due_date_label = tk.Label(self.frame, text="选择截止日期")
        self.due_date_label.pack(pady=5)
        self.calendar = Calendar(self.frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=5)

        # 按钮
        add_button = tk.Button(self.frame, text="添加目标", command=self.add_goal)
        add_button.pack(pady=5)

        view_button = tk.Button(self.frame, text="查看目标", command=self.view_goals)
        view_button.pack(pady=5)

        self.goal_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.goal_listbox.pack(pady=10)

    def add_goal(self):
        goal_text = self.goal_entry.get().strip()
        due_date_text = self.calendar.get_date()  # 从日历获取日期

        if not goal_text:
            messagebox.showwarning("输入错误", "请输入目标内容。")
            return

        goal = {"text": goal_text, "due_date": due_date_text, "completed": False}
        self.goals.append(goal)
        self.goal_listbox.insert(tk.END, f"目标: {goal_text} 截止日期: {due_date_text}")
        self.goal_entry.delete(0, tk.END)

    def view_goals(self):
        if not self.goals:
            messagebox.showinfo("无目标", "当前没有设置目标。")
        else:
            for goal in self.goals:
                status = "已完成" if goal["completed"] else "未完成"
                print(f"目标: {goal['text']}, 截止日期: {goal['due_date']}, 状态: {status}")
