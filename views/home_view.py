# views/home_view.py
import tkinter as tk
from tkinter import messagebox, ttk
from models import Project, AbilityTag
from utils import display_error, display_info, display_warning
from tkcalendar import Calendar
from datetime import datetime

class HomeView:
    def __init__(self, parent, data_manager, abilities):
        """
        初始化主页视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        :param abilities: 可用的能力标签列表（List of AbilityTag objects）
        """
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities
        self.tasks = self.data_manager.load_tasks()
        self.projects = self.data_manager.load_projects()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Treeview（任务列表）
        columns = ("Name", "Due Date", "Abilities", "Description", "Progress", "Mark as Project")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Description":
                self.tree.column(col, width=200)
            elif col == "Progress":
                self.tree.column(col, width=100)
            elif col == "Mark as Project":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=100)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # 添加任务到 Treeview
        for task in self.tasks:
            abilities_str = ", ".join([ability.name for ability in task.ability]) if task.ability else "无"
            self.tree.insert('', tk.END, values=(
                task.name,
                task.due_date,
                abilities_str,
                task.description,
                f"{task.progress}%",
                "是"  # 作为项目的标记
            ))

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            task_values = item['values']
            task_name = task_values[0]

            # 找到对应的任务对象
            task = next((t for t in self.tasks if t.name == task_name), None)
            if task:
                self.mark_task_as_project(task)
            else:
                messagebox.showerror("错误", "未找到选中的任务。")
        else:
            messagebox.showwarning("警告", "请选择要标记为项目的任务。")

    def mark_task_as_project(self, task):
        """
        将任务标记为项目。

        :param task: Task 对象
        """
        # 创建项目名称
        project_name = f"项目 - {task.name}"

        # 检查项目是否已存在
        if any(p.name == project_name for p in self.projects):
            messagebox.showinfo("提示", "该任务已被标记为项目。")
            return

        # 创建项目对象
        # 确保 abilities 是 AbilityTag 对象的列表
        if task.ability:
            abilities = [task.ability]  # 将单个 AbilityTag 对象转换为列表
        else:
            abilities = []

        new_project = Project(
            name=project_name,
            due_date=task.due_date,
            abilities=abilities,
            description=task.description,
            progress=task.progress,
            interest=task.interest
        )

        # 添加到项目列表
        self.projects.append(new_project)

        # 保存项目
        try:
            self.data_manager.save_projects(self.projects)
            display_info("成功", f"任务 '{task.name}' 已被标记为项目。")
        except Exception as e:
            print(f"保存项目时出错: {e}")
            display_error("错误", "保存项目时出错。")

        # 更新主页界面（可选）
        # 例如，移除已标记为项目的任务，或者更新状态
        self.refresh_treeview()

    def refresh_treeview(self):
        """
        刷新任务列表的Treeview。
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.tasks:
            abilities_str = ", ".join([ability.name for ability in task.ability]) if task.ability else "无"
            self.tree.insert('', tk.END, values=(
                task.name,
                task.due_date,
                abilities_str,
                task.description,
                f"{task.progress}%",
                "是"  # 作为项目的标记
            ))
