# views/daily_progress_view.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import Calendar
from models import DailyProgress, AbilityTag, Task
from utils import display_error, display_info
from datetime import datetime, timedelta
import webbrowser

class DailyProgressView:
    def __init__(self, parent, data_manager, abilities):
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities  # List of AbilityTag objects
        self.daily_progress_list = self.data_manager.load_daily_progress()
        self.tasks = self.data_manager.load_tasks()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()
        self.refresh_treeview()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        # 使用自定义样式的按钮
        style = ttk.Style()
        style.configure("Rounded.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=10,
                        relief="flat",
                        background="#4CAF50",
                        foreground="white")
        style.map("Rounded.TButton",
                  background=[("active", "#388E3C")])

        # 添加/编辑备注按钮
        add_note_button = ttk.Button(buttons_frame, text="添加/编辑备注", command=self.add_edit_note, style="Rounded.TButton")
        add_note_button.pack(side=tk.LEFT, padx=5)

        # Treeview（每日进度列表）
        columns = ("Date", "Tasks Completed", "Completed Tasks Details", "Notes", "Tags")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')

        # 定义列
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Completed Tasks Details":
                self.tree.column(col, width=150, anchor='center')
            elif col == "Notes":
                self.tree.column(col, width=300, anchor='w')
            else:
                self.tree.column(col, width=150, anchor='center')

        # 应用样式
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 11, "bold"), foreground="#4CAF50")
        style.configure("Treeview", font=("Microsoft YaHei", 10), rowheight=25)
        style.map("Treeview", background=[("selected", "#e0f7fa")])

        # 添加斑马条纹
        self.tree.tag_configure('oddrow', background='#f9f9f9')
        self.tree.tag_configure('evenrow', background='#e0f0f5')

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_single_click)

    def refresh_treeview(self):
        # 同步每日进度
        self.data_manager.synchronize_daily_progress()
        self.daily_progress_list = self.data_manager.load_daily_progress()
        self.tasks = self.data_manager.load_tasks()

        # 清空现有的树视图内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 按日期排序
        sorted_progress = sorted(self.daily_progress_list, key=lambda dp: dp.progress_date, reverse=True)
        
        # 预计算每个日期完成的任务及其详情
        self.completed_tasks_details = {}
        for entry in sorted_progress:
            completed_tasks = self.get_tasks_completed_on(entry.progress_date)
            self.completed_tasks_details[entry.progress_date] = completed_tasks

            # 更新 tasks_completed 为当天完成的任务数
            entry.tasks_completed = len(completed_tasks)

        # 插入数据到Treeview，应用斑马条纹
        for idx, entry in enumerate(sorted_progress):
            tags_str = ", ".join([tag.name for tag in entry.tags]) if entry.tags else "无"
            notes_preview = entry.notes if entry.notes else "无"
            row_tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=(
                entry.progress_date,
                entry.tasks_completed,
                "查看详情",
                notes_preview,
                tags_str
            ), tags=(row_tag,))

    def get_tasks_completed_on(self, date_str):
        """
        获取某天完成的所有任务。
        """
        completed_tasks = []
        for task in self.tasks:
            for progress_entry in task.progress_history:
                timestamp, description, progress = progress_entry
                entry_date = timestamp.split(' ')[0]  # 提取日期部分
                if entry_date == date_str and progress == 100:
                    completed_tasks.append(task.name)
                    break  # 一个任务只计一次
        return completed_tasks

    def add_edit_note(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            progress_date = values[0]
            entry = next((e for e in self.daily_progress_list if e.progress_date == progress_date), None)

            if not entry:
                display_error("未找到选中的每日进度。")
                return

            # 弹出对话框以编辑备注
            new_note = simpledialog.askstring("添加/编辑备注", f"为 {progress_date} 添加或编辑备注:", initialvalue=entry.notes, parent=self.parent)
            if new_note is not None:
                entry.notes = new_note.strip()
                self.data_manager.save_daily_progress(self.daily_progress_list)
                self.refresh_treeview()
                display_info("成功", "备注已更新。")
        else:
            messagebox.showwarning("警告", "请选择要添加/编辑备注的每日进度！")

    def on_double_click(self, event):
        # 获取被双击的项目
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return

        # 获取列索引（1-based）
        col_index = int(column.replace("#", ""))
        # 如果双击的是 "Completed Tasks Details" 列（第三列）
        if col_index == 3:
            values = self.tree.item(item_id, 'values')
            progress_date = values[0]
            completed_tasks = self.completed_tasks_details.get(progress_date, [])

            if not completed_tasks:
                display_info("信息", f"{progress_date} 没有完成的任务。")
                return

            # 打开一个新窗口显示完成的任务
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"{progress_date} 完成的任务")
            detail_window.grab_set()

            # 使用Notebook分隔任务和详细信息
            notebook = ttk.Notebook(detail_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)

            # 任务列表页
            tasks_frame = ttk.Frame(notebook)
            notebook.add(tasks_frame, text="任务列表")

            ttk.Label(tasks_frame, text=f"{progress_date} 完成的任务:", font=("Microsoft YaHei", 12, "bold")).pack(pady=10)

            tasks_listbox = tk.Listbox(tasks_frame, font=("Microsoft YaHei", 11), width=50, selectbackground="#4CAF50")
            tasks_listbox.pack(fill='both', expand=True, padx=10, pady=10)

            for task in completed_tasks:
                tasks_listbox.insert(tk.END, task)

            # 任务详细信息页（可扩展）
            details_frame = ttk.Frame(notebook)
            notebook.add(details_frame, text="任务详情")

            if completed_tasks:
                selected_task = completed_tasks[0]
                task = next((t for t in self.tasks if t.name == selected_task), None)
                if task:
                    ttk.Label(details_frame, text=f"任务名称: {task.name}", font=("Microsoft YaHei", 12)).pack(pady=5, anchor='w')
                    ttk.Label(details_frame, text=f"描述: {task.description}", font=("Microsoft YaHei", 12)).pack(pady=5, anchor='w')
                    ttk.Label(details_frame, text=f"关联能力标签: {', '.join([tag.name for tag in task.abilities]) if task.abilities else '无'}", font=("Microsoft YaHei", 12)).pack(pady=5, anchor='w')

            close_button = ttk.Button(detail_window, text="关闭", command=detail_window.destroy, style="Rounded.TButton")
            close_button.pack(pady=10)

    def on_single_click(self, event):
        """
        防止双击时触发单击事件。
        """
        pass  # 目前不需要处理单击事件，可以保留以便未来扩展

    def get_tasks_completed_on_date(self, date_str):
        """
        获取某一天完成的任务列表。
        """
        return self.completed_tasks_details.get(date_str, [])
