# views/goals_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from models import Goal

class GoalsView:
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.goals = self.data_manager.load_goals()  # 从 DataManager 加载目标
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

        # 按钮框架
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=5)

        add_button = tk.Button(button_frame, text="添加目标", command=self.add_goal)
        add_button.grid(row=0, column=0, padx=5)

        modify_button = tk.Button(button_frame, text="修改目标", command=self.modify_goal)
        modify_button.grid(row=0, column=1, padx=5)

        delete_button = tk.Button(button_frame, text="删除目标", command=self.delete_goal)
        delete_button.grid(row=0, column=2, padx=5)

        view_button = tk.Button(button_frame, text="查看目标", command=self.view_goals)
        view_button.grid(row=0, column=3, padx=5)

        self.goal_listbox = tk.Listbox(self.frame, width=70, height=15)
        self.goal_listbox.pack(pady=10)

        # 初始加载目标到 Listbox
        self.populate_listbox()

    def populate_listbox(self):
        """将目标列表显示在 Listbox 中"""
        self.goal_listbox.delete(0, tk.END)
        for idx, goal in enumerate(self.goals, start=1):
            status = "已完成" if goal.completed else "未完成"
            self.goal_listbox.insert(tk.END, f"{idx}. 目标: {goal.text} 截止日期: {goal.due_date} 状态: {status}")

    def add_goal(self):
        goal_text = self.goal_entry.get().strip()
        due_date_text = self.calendar.get_date()  # 从日历获取日期

        if not goal_text:
            messagebox.showwarning("输入错误", "请输入目标内容。")
            return

        # 检查日期格式
        try:
            datetime.strptime(due_date_text, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("日期错误", "请选择有效的截止日期。")
            return

        goal = Goal(text=goal_text, due_date=due_date_text, completed=False)
        self.goals.append(goal)
        self.data_manager.save_goals(self.goals)  # 通过 DataManager 保存目标
        self.populate_listbox()
        self.goal_entry.delete(0, tk.END)

    def delete_goal(self):
        selected_indices = self.goal_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("选择错误", "请选择要删除的目标。")
            return

        index = selected_indices[0]
        goal = self.goals[index]

        confirm = messagebox.askyesno("确认删除", f"确定要删除目标: '{goal.text}' 吗？")
        if confirm:
            del self.goals[index]
            self.data_manager.save_goals(self.goals)
            self.populate_listbox()

    def modify_goal(self):
        selected_indices = self.goal_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("选择错误", "请选择要修改的目标。")
            return

        index = selected_indices[0]
        goal = self.goals[index]

        # 创建一个新窗口用于修改目标
        modify_window = tk.Toplevel(self.parent)
        modify_window.title("修改目标")
        modify_window.geometry("400x450")

        # 目标内容输入框
        tk.Label(modify_window, text="目标内容:", font=("Microsoft YaHei", 12)).pack(pady=5)
        goal_text_entry = tk.Entry(modify_window, width=50)
        goal_text_entry.pack(pady=5)
        goal_text_entry.insert(0, goal.text)

        # 截止日期选择器
        tk.Label(modify_window, text="选择截止日期:", font=("Microsoft YaHei", 12)).pack(pady=5)
        modify_calendar = Calendar(modify_window, selectmode='day', date_pattern='yyyy-mm-dd')
        modify_calendar.pack(pady=5)
        try:
            modify_calendar.set_date(goal.due_date)  # 使用 set_date 设置日期
        except AttributeError:
            # 如果 set_date 方法不存在，尝试使用 selection_set
            modify_calendar.selection_set(goal.due_date)

        # 完成状态复选框
        completed_var = tk.BooleanVar(value=goal.completed)
        completed_check = tk.Checkbutton(modify_window, text="已完成", variable=completed_var)
        completed_check.pack(pady=5)

        # 保存按钮
        def save_changes():
            new_text = goal_text_entry.get().strip()
            new_due_date = modify_calendar.get_date()
            new_completed = completed_var.get()

            if not new_text:
                messagebox.showwarning("输入错误", "目标内容不能为空。")
                return

            # 验证日期格式
            try:
                datetime.strptime(new_due_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("日期错误", "请选择有效的截止日期。")
                return

            # 确认更改截止日期
            if new_due_date != goal.due_date:
                confirm = messagebox.askyesno("确认更改", "您确定要更改截止日期吗？")
                if not confirm:
                    return  # 如果用户选择取消，则不保存更改

            # 更新目标
            goal.text = new_text
            goal.due_date = new_due_date
            goal.completed = new_completed

            self.data_manager.save_goals(self.goals)
            self.populate_listbox()
            modify_window.destroy()
            messagebox.showinfo("成功", "目标已更新。")

        save_button = tk.Button(modify_window, text="保存更改", command=save_changes)
        save_button.pack(pady=10)

    def view_goals(self):
        if not self.goals:
            messagebox.showinfo("无目标", "当前没有设置目标。")
        else:
            # 创建一个新窗口显示目标详情
            view_window = tk.Toplevel(self.parent)
            view_window.title("目标列表")
            view_window.geometry("500x400")

            canvas = tk.Canvas(view_window)
            scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for goal in self.goals:
                status = "已完成" if goal.completed else "未完成"
                goal_frame = ttk.Frame(scrollable_frame, padding=10)
                goal_frame.pack(fill='x', pady=5, padx=10, anchor='w')

                goal_label = tk.Label(goal_frame, text=f"目标: {goal.text}", font=("Microsoft YaHei", 12, "bold"))
                goal_label.pack(anchor='w')

                due_date_label = tk.Label(goal_frame, text=f"截止日期: {goal.due_date}", font=("Microsoft YaHei", 10))
                due_date_label.pack(anchor='w')

                status_label = tk.Label(goal_frame, text=f"状态: {status}", font=("Microsoft YaHei", 10))
                status_label.pack(anchor='w')

            close_button = tk.Button(view_window, text="关闭", command=view_window.destroy)
            close_button.pack(pady=10)
