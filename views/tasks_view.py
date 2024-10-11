# views/tasks_view.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import Calendar
from models import Task, Project, AbilityTag  # 导入 Project 类
from utils import display_error, display_info
from datetime import datetime

class TasksView:
    def __init__(self, parent, data_manager, abilities):
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities  # List of AbilityTag objects
        self.tasks = self.data_manager.load_tasks()
        self.projects = self.data_manager.load_projects()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.sorting_order = {}  # 记录每个列的排序顺序

        self.create_widgets()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_button = tk.Button(buttons_frame, text="添加任务", command=self.open_add_task_window)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(buttons_frame, text="修改任务", command=self.edit_task)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(buttons_frame, text="删除任务", command=self.delete_task)
        delete_button.pack(side=tk.LEFT, padx=5)

        update_progress_button = tk.Button(buttons_frame, text="更新进度", command=self.update_progress)
        update_progress_button.pack(side=tk.LEFT, padx=5)

        # Treeview（任务列表）
        columns = ("Name", "Due Date", "Interest", "Ability", "Description", "Progress", "Type")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            if col in ["Interest", "Progress", "Due Date"]:
                self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col))
            else:
                self.tree.heading(col, text=col)
            if col == "Description":
                self.tree.column(col, width=200)
            elif col == "Progress":
                self.tree.column(col, width=100)
            elif col == "Type":
                self.tree.column(col, width=80)
            elif col == "Due Date":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=100)

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_treeview()

        # 绑定双击事件以查看详情
        self.tree.bind("<Double-1>", self.on_double_click)

    def refresh_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.tasks:
            interest = task.interest if task.interest else 0
            stars = '★' * interest + '☆' * (5 - interest)
            task_type = "任务"
            abilities_str = ", ".join([ability.name for ability in task.abilities]) if task.abilities else "无"
            self.tree.insert('', tk.END, values=(
                task.name,
                task.due_date,
                stars,
                abilities_str,
                task.description,
                f"{task.progress}%",
                task_type
            ))
        for project in self.projects:
            interest = project.interest if project.interest else 0
            stars = '★' * interest + '☆' * (5 - interest)
            abilities_str = ", ".join([ability.name for ability in project.abilities]) if project.abilities else "无"
            self.tree.insert('', tk.END, values=(
                project.name,
                project.due_date,
                stars,
                abilities_str,
                project.description,
                f"{project.progress}%",
                "项目"
            ))

    def sort_treeview(self, col):
        # Determine sort order
        if col in self.sorting_order and self.sorting_order[col] == "asc":
            reverse = True
            self.sorting_order[col] = "desc"
        else:
            reverse = False
            self.sorting_order[col] = "asc"

        # Fetch all items and sort them
        data = []
        for child in self.tree.get_children(''):
            val = self.tree.set(child, col)
            data.append((val, child))

        if col == "Interest":
            # Sort based on number of stars
            data.sort(key=lambda t: t[0].count('★'), reverse=reverse)
        elif col == "Progress":
            # Sort numerically
            try:
                data.sort(key=lambda t: int(t[0].strip('%')), reverse=reverse)
            except ValueError:
                data.sort(key=lambda t: t[0], reverse=reverse)
        elif col == "Due Date":
            # Sort by date
            try:
                data.sort(key=lambda t: datetime.strptime(t[0], '%Y-%m-%d'), reverse=reverse)
            except ValueError:
                data.sort(key=lambda t: t[0], reverse=reverse)
        else:
            # For other columns, sort alphabetically
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

    def on_double_click(self, event):
        self.view_task()

    def open_add_task_window(self):
        add_window = tk.Toplevel(self.parent)
        add_window.title("添加新任务")
        add_window.grab_set()  # 模态窗口

        # 任务名称
        tk.Label(add_window, text="任务名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = tk.Entry(add_window, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # 截止日期
        tk.Label(add_window, text="截止日期:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        cal = Calendar(add_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.grid(row=1, column=1, padx=10, pady=5)

        # 感兴趣程度
        tk.Label(add_window, text="感兴趣程度:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        interest_var = tk.IntVar(value=3)
        interest_spin = tk.Spinbox(add_window, from_=1, to=5, textvariable=interest_var, width=5)
        interest_spin.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # 能力标签搜索框
        tk.Label(add_window, text="搜索能力标签:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        search_entry = tk.Entry(add_window, width=30)
        search_entry.grid(row=3, column=1, padx=10, pady=5)

        # 能力标签列表框
        tk.Label(add_window, text="能力标签:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

        abilities_var = tk.Variable(value=[tag.name for tag in self.abilities])
        abilities_listbox = tk.Listbox(add_window, listvariable=abilities_var, selectmode='multiple', height=5)
        abilities_listbox.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        # 添加能力标签按钮
        add_ability_button = tk.Button(add_window, text="添加能力标签", command=lambda: self.add_ability_tag(add_window))
        add_ability_button.grid(row=4, column=2, padx=5, pady=5)

        # 实现搜索功能
        def search_abilities(event):
            search_term = search_entry.get().lower()
            filtered_abilities = [tag.name for tag in self.abilities if search_term in tag.name.lower()]
            abilities_var.set(filtered_abilities)

        search_entry.bind("<KeyRelease>", search_abilities)  # 动态搜索功能

        # 详细描述
        tk.Label(add_window, text="详细描述:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.NW)
        description_text = tk.Text(add_window, width=30, height=5)
        description_text.grid(row=5, column=1, padx=10, pady=5)

        # 添加按钮
        def add_task():
            name = name_entry.get().strip()
            due_date = cal.get_date()
            try:
                interest = int(interest_var.get())
            except ValueError:
                interest = 0

            selected_indices = abilities_listbox.curselection()
            selected_abilities = [self.abilities[i] for i in selected_indices]
            description = description_text.get("1.0", tk.END).strip()

            if not name:
                messagebox.showwarning("警告", "任务名称不能为空！")
                return

            new_task = Task(name, due_date, interest, description, abilities=selected_abilities, progress=0)
            self.tasks.append(new_task)
            self.data_manager.save_tasks(self.tasks)
            self.refresh_treeview()
            add_window.destroy()
            display_info("成功", "任务已添加。")

        add_button = tk.Button(add_window, text="添加", command=add_task)
        add_button.grid(row=6, column=0, columnspan=3, pady=10)

    def add_ability_tag(self, parent_window, abilities_listbox=None):
        new_tag = simpledialog.askstring("添加能力标签", "请输入新的能力标签:", parent=parent_window)
        if new_tag:
            if any(ability.name == new_tag for ability in self.abilities):
                messagebox.showinfo("提示", "该能力标签已存在。")
            else:
                new_ability = AbilityTag(new_tag)
                self.abilities.append(new_ability)
                self.data_manager.save_abilities(self.abilities)
                display_info("成功", "能力标签已添加。")
                # 更新 Listbox 中的能力标签
                if abilities_listbox:
                    abilities_listbox.insert(tk.END, new_tag)
                else:
                    # If no specific listbox is provided, update all listboxes in the parent window
                    children = parent_window.winfo_children()
                    for widget in children:
                        if isinstance(widget, tk.Listbox):
                            abilities_var = tk.Variable(value=[ability.name for ability in self.abilities])
                            widget.config(listvariable=abilities_var)
                            break

    def edit_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            task_name = values[0]
            task_type = values[-1]
            if task_type == "项目":
                task = next((p for p in self.projects if p.name == task_name), None)
            else:
                task = next((t for t in self.tasks if t.name == task_name), None)

            if not task:
                display_error("错误", "未找到选中的任务。")
                return

            edit_window = tk.Toplevel(self.parent)
            edit_window.title("修改任务")
            edit_window.grab_set()  # 模态窗口

            # 任务名称
            tk.Label(edit_window, text="任务名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            name_entry = tk.Entry(edit_window, width=40)
            name_entry.insert(0, task.name)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            # 截止日期
            tk.Label(edit_window, text="截止日期:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            cal = Calendar(edit_window, selectmode='day', date_pattern='yyyy-mm-dd')
            cal.selection_set(task.due_date)
            cal.grid(row=1, column=1, padx=10, pady=5)

            # 感兴趣程度
            tk.Label(edit_window, text="感兴趣程度:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            interest_var = tk.IntVar(value=task.interest if task.interest else 0)
            interest_spin = tk.Spinbox(edit_window, from_=1, to=5, textvariable=interest_var, width=5)
            interest_spin.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

            # 能力标签
            tk.Label(edit_window, text="能力标签:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)

            # 搜索能力标签
            search_label = tk.Label(edit_window, text="搜索能力标签:")
            search_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            search_entry = tk.Entry(edit_window, width=30)
            search_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

            # 能力标签列表框
            abilities_var = tk.Variable(value=[tag.name for tag in self.abilities])
            abilities_listbox = tk.Listbox(edit_window, listvariable=abilities_var, selectmode='multiple', height=5)
            abilities_listbox.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

            # 预先选择当前任务的能力标签
            current_ability_names = [ability.name for ability in task.abilities]
            for idx, ability in enumerate(self.abilities):
                if ability.name in current_ability_names:
                    abilities_listbox.select_set(idx)

            add_ability_button = tk.Button(edit_window, text="添加能力标签", command=lambda: self.add_ability_tag(edit_window, abilities_listbox))
            add_ability_button.grid(row=5, column=2, padx=5, pady=5)

            # 实现搜索功能
            def search_abilities(event):
                search_term = search_entry.get().lower()
                filtered_abilities = [tag.name for tag in self.abilities if search_term in tag.name.lower()]
                abilities_var.set(filtered_abilities)

            search_entry.bind("<KeyRelease>", search_abilities)

            # 类型（不可修改）
            tk.Label(edit_window, text="类型:").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
            tk.Label(edit_window, text=task_type).grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

            # 详细描述
            tk.Label(edit_window, text="详细描述:").grid(row=7, column=0, padx=10, pady=5, sticky=tk.NW)
            description_text = tk.Text(edit_window, width=30, height=5)
            description_text.insert("1.0", task.description)
            description_text.grid(row=7, column=1, padx=10, pady=5)

            # 保存按钮
            def save_changes():
                name = name_entry.get().strip()
                due_date = cal.get_date()
                try:
                    interest = int(interest_var.get())
                except ValueError:
                    interest = 0

                # 获取选择的多个能力标签
                selected_indices = abilities_listbox.curselection()
                selected_abilities = [self.abilities[i] for i in selected_indices]

                description = description_text.get("1.0", tk.END).strip()

                if not name:
                    messagebox.showwarning("警告", "任务名称不能为空！")
                    return

                # 检查任务名称是否重复（如果名称被更改）
                if name != task.name:
                    if task_type == "项目":
                        if any(p.name == name for p in self.projects):
                            messagebox.showwarning("警告", "该项目名称已存在！")
                            return
                    else:
                        if any(t.name == name for t in self.tasks):
                            messagebox.showwarning("警告", "该任务名称已存在！")
                            return

                task.name = name
                task.due_date = due_date
                task.interest = interest
                task.abilities = selected_abilities
                task.description = description

                if task_type == "项目":
                    self.data_manager.save_projects(self.projects)
                else:
                    self.data_manager.save_tasks(self.tasks)

                # 同步每日进度
                self.data_manager.synchronize_daily_progress()

                self.refresh_treeview()
                edit_window.destroy()
                display_info("成功", "任务已更新。")

            save_button = tk.Button(edit_window, text="保存修改", command=save_changes)
            save_button.grid(row=8, column=0, columnspan=3, pady=10)
        else:
            messagebox.showwarning("警告", "请选择要修改的任务！")

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            task_name = values[0]
            task_type = values[-1]
            if task_type == "项目":
                task_list = self.projects
            else:
                task_list = self.tasks

            task = next((t for t in task_list if t.name == task_name), None)
            if not task:
                display_error("错误", "未找到选中的任务。")
                return

            confirm = messagebox.askyesno("确认", f"确定要删除选中的{task_type}吗？")
            if confirm:
                task_list.remove(task)
                if task_type == "项目":
                    self.data_manager.save_projects(self.projects)
                else:
                    self.data_manager.save_tasks(self.tasks)

                # 同步每日进度
                self.data_manager.synchronize_daily_progress()

                self.refresh_treeview()
                display_info("成功", f"{task_type}已删除。")
        else:
            messagebox.showwarning("警告", "请选择要删除的任务！")

    def view_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            task_name = values[0]
            task_type = values[-1]
            if task_type == "项目":
                task = next((p for p in self.projects if p.name == task_name), None)
            else:
                task = next((t for t in self.tasks if t.name == task_name), None)

            if not task:
                display_error("错误", "未找到选中的任务。")
                return

            if task_type == "项目":
                abilities_str = ", ".join([ability.name for ability in task.abilities]) if task.abilities else "无"
                interest_str = f"{task.interest}★" if task.interest is not None else "无"
                progress_history_str = "\n".join([f"{ts}: {desc} ({prog}%)" for ts, desc, prog in task.progress_history]) if task.progress_history else "无"

                details = (
                    f"项目名称: {task.name}\n"
                    f"截止日期: {task.due_date}\n"
                    f"感兴趣程度: {interest_str}\n"
                    f"能力标签: {abilities_str}\n"
                    f"详细描述:\n{task.description}\n"
                    f"当前进度: {task.progress}%\n"
                    f"进度历史:\n{progress_history_str}"
                )
            else:
                abilities_str = ", ".join([ability.name for ability in task.abilities]) if task.abilities else "无"
                interest_str = f"{task.interest}★" if task.interest is not None else "无"
                progress_history_str = "\n".join([f"{ts}: {desc} ({prog}%)" for ts, desc, prog in task.progress_history]) if task.progress_history else "无"

                details = (
                    f"任务名称: {task.name}\n"
                    f"截止日期: {task.due_date}\n"
                    f"感兴趣程度: {interest_str}\n"
                    f"能力标签: {abilities_str}\n"
                    f"详细描述:\n{task.description}\n"
                    f"当前进度: {task.progress}%\n"
                    f"进度历史:\n{progress_history_str}"
                )

            messagebox.showinfo("任务详情", details)
        else:
            messagebox.showwarning("警告", "请选择要查看的任务！")

    def update_progress(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            task_name = values[0]
            task_type = values[-1]
            if task_type == "项目":
                task = next((p for p in self.projects if p.name == task_name), None)
            else:
                task = next((t for t in self.tasks if t.name == task_name), None)

            if not task:
                display_error("错误", "未找到选中的任务。")
                return

            progress_window = tk.Toplevel(self.parent)
            progress_window.title("更新进度")
            progress_window.grab_set()  # 模态窗口

            tk.Label(progress_window, text=f"更新任务: {task.name}").pack(padx=10, pady=10)

            tk.Label(progress_window, text="当前进度 (%):").pack(padx=10, pady=5)
            progress_var = tk.IntVar(value=task.progress)
            progress_scale = tk.Scale(progress_window, from_=0, to=100, orient=tk.HORIZONTAL, variable=progress_var)
            progress_scale.pack(padx=10, pady=5)

            tk.Label(progress_window, text="进度描述:").pack(padx=10, pady=5)
            description_entry = tk.Entry(progress_window, width=50)
            description_entry.pack(padx=10, pady=5)

            def save_progress():
                new_progress = progress_var.get()
                description = description_entry.get().strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 使用 datetime
                if not description:
                    messagebox.showwarning("警告", "进度描述不能为空！")
                    return

                task.progress = new_progress
                task.progress_history.append((timestamp, description, new_progress))

                if task_type == "项目":
                    self.data_manager.save_projects(self.projects)
                else:
                    self.data_manager.save_tasks(self.tasks)

                # 同步每日进度
                self.data_manager.synchronize_daily_progress()

                self.refresh_treeview()
                progress_window.destroy()
                display_info("成功", "进度已更新。")

            save_button = tk.Button(progress_window, text="保存", command=save_progress)
            save_button.pack(pady=10)
        else:
            messagebox.showwarning("警告", "请选择要更新进度的任务！")

    def manage_abilities(self):
        # 修复错误：display_error 需要两个参数
        display_error("错误", "请通过主界面访问能力标签管理功能。")
