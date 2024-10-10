# views/projects_view.py
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from models import Project, AbilityTag
from utils import display_error, display_info, display_warning
from tkcalendar import Calendar

class ProjectsView:
    def __init__(self, parent, data_manager, abilities):
        """
        初始化项目视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        :param abilities: 可用的能力标签列表（List of AbilityTag objects）
        """
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities  # List of AbilityTag objects
        self.projects = self.data_manager.load_projects()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_button = tk.Button(buttons_frame, text="添加项目", command=self.open_add_project_window)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(buttons_frame, text="修改项目", command=self.edit_project)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(buttons_frame, text="删除项目", command=self.delete_project)
        delete_button.pack(side=tk.LEFT, padx=5)

        view_button = tk.Button(buttons_frame, text="查看详情", command=self.view_project)
        view_button.pack(side=tk.LEFT, padx=5)

        # Treeview（项目列表）
        columns = ("Name", "Due Date", "Abilities", "Description", "Progress", "Interest")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Description":
                self.tree.column(col, width=200)
            elif col == "Progress":
                self.tree.column(col, width=100)
            elif col == "Interest":
                self.tree.column(col, width=80)
            else:
                self.tree.column(col, width=100)

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_treeview()

    def refresh_treeview(self):
        """
        刷新项目列表的Treeview。
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for project in self.projects:
            abilities_str = ", ".join([ability.name for ability in project.abilities])
            interest_str = f"{project.interest}★" if project.interest is not None else "无"
            self.tree.insert('', tk.END, values=(
                project.name,
                project.due_date,
                abilities_str,
                project.description,
                f"{project.progress}%",
                interest_str
            ))

    def open_add_project_window(self):
        """
        打开添加项目的窗口。
        """
        add_window = tk.Toplevel(self.parent)
        add_window.title("添加新项目")
        add_window.grab_set()  # 模态窗口

        # 项目名称
        tk.Label(add_window, text="项目名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = tk.Entry(add_window, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # 截止日期
        tk.Label(add_window, text="截止日期:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        cal = Calendar(add_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.grid(row=1, column=1, padx=10, pady=5)

        # 能力标签
        tk.Label(add_window, text="能力标签:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        abilities_var = tk.Variable(value=[ability.name for ability in self.abilities])
        abilities_listbox = tk.Listbox(add_window, listvariable=abilities_var, selectmode='multiple', height=5)
        abilities_listbox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        add_ability_button = tk.Button(add_window, text="添加能力标签", command=lambda: self.add_ability_tag(add_window))
        add_ability_button.grid(row=2, column=2, padx=5, pady=5)

        # 详细描述
        tk.Label(add_window, text="详细描述:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.NW)
        description_text = tk.Text(add_window, width=30, height=5)
        description_text.grid(row=3, column=1, padx=10, pady=5)

        # 进度
        tk.Label(add_window, text="进度 (%):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        progress_var = tk.IntVar(value=0)
        progress_scale = tk.Scale(add_window, from_=0, to=100, orient=tk.HORIZONTAL, variable=progress_var)
        progress_scale.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        # 感兴趣程度（可选）
        tk.Label(add_window, text="感兴趣程度 (可选, 1-5):").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        interest_var = tk.IntVar()
        interest_spin = tk.Spinbox(add_window, from_=1, to=5, textvariable=interest_var, width=5)
        interest_spin.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

        # 添加按钮
        def add_project():
            name = name_entry.get().strip()
            due_date = cal.get_date()
            selected_indices = abilities_listbox.curselection()
            selected_abilities = [self.abilities[i] for i in selected_indices]
            description = description_text.get("1.0", tk.END).strip()
            progress = progress_var.get()
            interest = interest_var.get() if interest_spin.get() else None

            if not name:
                messagebox.showwarning("警告", "项目名称不能为空！")
                return

            # 检查兴趣程度是否在1-5范围内
            if interest is not None:
                try:
                    interest = int(interest)
                    if not (1 <= interest <= 5):
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("警告", "感兴趣程度必须在1到5之间！")
                    return
            else:
                interest = None

            new_project = Project(name, due_date, selected_abilities, description, progress, interest)
            self.projects.append(new_project)
            self.data_manager.save_projects(self.projects)
            self.refresh_treeview()
            add_window.destroy()
            display_info("成功", "项目已添加。")

        add_button = tk.Button(add_window, text="添加", command=add_project)
        add_button.grid(row=6, column=0, columnspan=3, pady=10)

    def add_ability_tag(self, parent_window):
        """
        添加新的能力标签。

        :param parent_window: 父窗口
        """
        new_tag = simpledialog.askstring("添加能力标签", "请输入新的能力标签:", parent=parent_window)
        if new_tag:
            if any(ability.name == new_tag for ability in self.abilities):
                messagebox.showinfo("提示", "该能力标签已存在。")
            else:
                new_ability = AbilityTag(new_tag)
                self.abilities.append(new_ability)
                self.data_manager.save_abilities(self.abilities)
                display_info("成功", "能力标签已添加。")
                # 更新列表框中的能力标签
                children = parent_window.winfo_children()
                for widget in children:
                    if isinstance(widget, tk.Listbox):
                        abilities_var = tk.Variable(value=[ability.name for ability in self.abilities])
                        widget.config(listvariable=abilities_var)
                        break

    def edit_project(self):
        """
        编辑选中的项目。
        """
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            project = self.projects[item_index]

            edit_window = tk.Toplevel(self.parent)
            edit_window.title("修改项目")
            edit_window.grab_set()  # 模态窗口

            # 项目名称
            tk.Label(edit_window, text="项目名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            name_entry = tk.Entry(edit_window, width=40)
            name_entry.insert(0, project.name)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            # 截止日期
            tk.Label(edit_window, text="截止日期:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            cal = Calendar(edit_window, selectmode='day', date_pattern='yyyy-mm-dd')
            cal.set_date(project.due_date)
            cal.grid(row=1, column=1, padx=10, pady=5)

            # 能力标签
            tk.Label(edit_window, text="能力标签:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            abilities_var = tk.Variable(value=[ability.name for ability in self.abilities])
            abilities_listbox = tk.Listbox(edit_window, listvariable=abilities_var, selectmode='multiple', height=5)
            abilities_listbox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

            # 预先选择当前项目的能力标签
            current_ability_names = [ability.name for ability in project.abilities]
            for idx, ability in enumerate(self.abilities):
                if ability.name in current_ability_names:
                    abilities_listbox.select_set(idx)

            add_ability_button = tk.Button(edit_window, text="添加能力标签", command=lambda: self.add_ability_tag(edit_window))
            add_ability_button.grid(row=2, column=2, padx=5, pady=5)

            # 详细描述
            tk.Label(edit_window, text="详细描述:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.NW)
            description_text = tk.Text(edit_window, width=30, height=5)
            description_text.insert("1.0", project.description)
            description_text.grid(row=3, column=1, padx=10, pady=5)

            # 进度
            tk.Label(edit_window, text="进度 (%):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            progress_var = tk.IntVar(value=project.progress)
            progress_scale = tk.Scale(edit_window, from_=0, to=100, orient=tk.HORIZONTAL, variable=progress_var)
            progress_scale.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

            # 感兴趣程度（可选）
            tk.Label(edit_window, text="感兴趣程度 (可选, 1-5):").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
            interest_var = tk.IntVar(value=project.interest if project.interest is not None else 0)
            interest_spin = tk.Spinbox(edit_window, from_=1, to=5, textvariable=interest_var, width=5)
            interest_spin.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

            # 保存按钮
            def save_changes():
                name = name_entry.get().strip()
                due_date = cal.get_date()
                selected_indices = abilities_listbox.curselection()
                selected_abilities = [self.abilities[i] for i in selected_indices]
                description = description_text.get("1.0", tk.END).strip()
                progress = progress_var.get()
                interest = interest_var.get() if interest_spin.get() else None

                if not name:
                    messagebox.showwarning("警告", "项目名称不能为空！")
                    return

                # 检查兴趣程度是否在1-5范围内
                if interest is not None and interest != 0:
                    try:
                        interest = int(interest)
                        if not (1 <= interest <= 5):
                            raise ValueError
                    except ValueError:
                        messagebox.showwarning("警告", "感兴趣程度必须在1到5之间！")
                        return
                else:
                    interest = None

                project.name = name
                project.due_date = due_date
                project.abilities = selected_abilities
                project.description = description
                project.progress = progress
                project.interest = interest

                self.data_manager.save_projects(self.projects)
                self.refresh_treeview()
                edit_window.destroy()
                display_info("成功", "项目已更新。")

            save_button = tk.Button(edit_window, text="保存修改", command=save_changes)
            save_button.grid(row=6, column=0, columnspan=3, pady=10)
        else:
            messagebox.showwarning("警告", "请选择要修改的项目！")

    def delete_project(self):
        """
        删除选中的项目。
        """
        selected_item = self.tree.selection()
        if selected_item:
            confirm = messagebox.askyesno("确认", "确定要删除选中的项目吗？")
            if confirm:
                item_index = self.tree.index(selected_item)
                del self.projects[item_index]
                self.data_manager.save_projects(self.projects)
                self.refresh_treeview()
                display_info("成功", "项目已删除。")
        else:
            messagebox.showwarning("警告", "请选择要删除的项目！")

    def view_project(self):
        """
        查看选中的项目详情。
        """
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            project = self.projects[item_index]

            view_window = tk.Toplevel(self.parent)
            view_window.title(f"项目详情: {project.name}")
            view_window.grab_set()  # 模态窗口

            # 标题
            tk.Label(view_window, text=f"项目名称: {project.name}", font=('Arial', 14, 'bold')).pack(padx=10, pady=5)
            tk.Label(view_window, text=f"截止日期: {project.due_date}", font=('Arial', 12)).pack(padx=10, pady=5)

            # 能力标签
            abilities_str = ", ".join([ability.name for ability in project.abilities])
            tk.Label(view_window, text=f"能力标签: {abilities_str}", font=('Arial', 12)).pack(padx=10, pady=5)

            # 详细描述
            tk.Label(view_window, text="详细描述:", font=('Arial', 12, 'bold')).pack(padx=10, pady=5, anchor=tk.W)
            description_text = tk.Text(view_window, width=60, height=10)
            description_text.pack(padx=10, pady=5)
            description_text.insert("1.0", project.description)
            description_text.config(state='disabled')  # 只读

            # 进度
            tk.Label(view_window, text=f"当前进度: {project.progress}%", font=('Arial', 12)).pack(padx=10, pady=5)

            # 感兴趣程度
            if project.interest is not None:
                interest_str = f"{project.interest}★"
            else:
                interest_str = "无"
            tk.Label(view_window, text=f"感兴趣程度: {interest_str}", font=('Arial', 12)).pack(padx=10, pady=5)

            close_button = tk.Button(view_window, text="关闭", command=view_window.destroy)
            close_button.pack(pady=10)
        else:
            messagebox.showwarning("警告", "请选择要查看的项目！")
