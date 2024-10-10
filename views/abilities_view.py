# views/abilities_view.py
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from models import AbilityTag
from utils import display_error, display_info
from datetime import datetime, date
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AbilitiesView:
    def __init__(self, parent, data_manager):
        """
        初始化能力标签视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        """
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = self.data_manager.load_abilities()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # 搜索框架
        search_frame = tk.Frame(self.frame)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="搜索能力标签:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(search_frame, text="搜索", command=self.search_abilities)
        search_button.pack(side=tk.LEFT, padx=5)

        reset_button = tk.Button(search_frame, text="重置", command=self.reset_search)
        reset_button.pack(side=tk.LEFT, padx=5)

        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_button = tk.Button(buttons_frame, text="添加能力标签", command=self.add_ability)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(buttons_frame, text="编辑能力标签", command=self.edit_ability)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(buttons_frame, text="删除能力标签", command=self.delete_ability)
        delete_button.pack(side=tk.LEFT, padx=5)

        visualize_button = tk.Button(buttons_frame, text="图形化展示", command=self.visualize_abilities)
        visualize_button.pack(side=tk.LEFT, padx=5)

        # Treeview（能力标签树）
        self.tree = ttk.Treeview(self.frame, show='tree', selectmode='browse')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_treeview()

    def search_abilities(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("警告", "请输入搜索关键字！")
            return
        self.refresh_treeview(search_term=search_term)

    def reset_search(self):
        self.search_var.set('')
        self.refresh_treeview()

    def refresh_treeview(self, search_term=None):
        """
        刷新能力标签的 Treeview，以树状结构展示。
        如果提供了搜索关键字，只显示匹配的节点。
        """
        # 清空当前的树
        self.tree.delete(*self.tree.get_children())

        # 创建一个字典，用于快速查找能力标签
        ability_dict = {ability.name: ability for ability in self.abilities}

        # 创建一个字典，存储每个节点的 Treeview item ID
        tree_items = {}

        # 定义一个函数，用于判断能力标签是否匹配搜索关键字
        def matches_search(ability):
            if not search_term:
                return True
            return search_term.lower() in ability.name.lower()

        # 递归地添加子节点
        def add_children(parent_ability, parent_item):
            children = [ability for ability in self.abilities if ability.parent == parent_ability.name]
            for child in children:
                # 如果子节点或其子孙节点匹配搜索，则添加到树中
                if matches_search(child) or has_matching_descendant(child):
                    child_item = self.tree.insert(parent_item, 'end', text=child.name, values=(child.name,))
                    tree_items[child.name] = child_item
                    add_children(child, child_item)

        # 定义一个函数，判断子孙节点是否有匹配搜索关键字的
        def has_matching_descendant(ability):
            children = [a for a in self.abilities if a.parent == ability.name]
            for child in children:
                if matches_search(child) or has_matching_descendant(child):
                    return True
            return False

        # 添加根节点及其子节点
        roots = [ability for ability in self.abilities if not ability.parent]
        for root in roots:
            # 如果根节点或其子孙节点匹配搜索，则添加到树中
            if matches_search(root) or has_matching_descendant(root):
                root_item = self.tree.insert('', 'end', text=root.name, values=(root.name,))
                tree_items[root.name] = root_item
                add_children(root, root_item)

    def add_ability(self):
        """
        添加新的能力标签。
        """
        add_window = tk.Toplevel(self.parent)
        add_window.title("添加能力标签")
        add_window.grab_set()  # 模态窗口

        # 能力名称
        tk.Label(add_window, text="能力名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = tk.Entry(add_window, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # 父能力标签
        tk.Label(add_window, text="父能力标签:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        parent_var = tk.StringVar()
        parent_combobox = ttk.Combobox(add_window, textvariable=parent_var, values=["无"] + [ability.name for ability in self.abilities], state='readonly')
        parent_combobox.grid(row=1, column=1, padx=10, pady=5)
        parent_combobox.set("无")

        # 添加按钮
        def save_ability():
            name = name_entry.get().strip()
            parent = parent_var.get()
            if parent == "无":
                parent = None

            if not name:
                messagebox.showwarning("警告", "能力名称不能为空！")
                return

            if any(ability.name == name for ability in self.abilities):
                messagebox.showwarning("警告", "该能力标签已存在！")
                return

            new_ability = AbilityTag(name, parent)
            self.abilities.append(new_ability)
            self.data_manager.save_abilities(self.abilities)
            self.refresh_treeview()
            add_window.destroy()
            display_info("成功", "能力标签已添加。")

        save_button = tk.Button(add_window, text="保存", command=save_ability)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def edit_ability(self):
        """
        编辑选中的能力标签。
        """
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            ability = next((a for a in self.abilities if a.name == selected_name), None)

            if not ability:
                messagebox.showwarning("警告", "未找到选中的能力标签！")
                return

            edit_window = tk.Toplevel(self.parent)
            edit_window.title("编辑能力标签")
            edit_window.grab_set()  # 模态窗口

            # 能力名称
            tk.Label(edit_window, text="能力名称:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            name_entry = tk.Entry(edit_window, width=40)
            name_entry.insert(0, ability.name)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            # 父能力标签
            tk.Label(edit_window, text="父能力标签:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            parent_var = tk.StringVar()
            parent_combobox = ttk.Combobox(edit_window, textvariable=parent_var, values=["无"] + [a.name for a in self.abilities if a.name != ability.name], state='readonly')
            parent_combobox.grid(row=1, column=1, padx=10, pady=5)
            parent_combobox.set(ability.parent if ability.parent else "无")

            # 添加按钮
            def save_changes():
                new_name = name_entry.get().strip()
                new_parent = parent_var.get()
                if new_parent == "无":
                    new_parent = None

                if not new_name:
                    messagebox.showwarning("警告", "能力名称不能为空！")
                    return

                if new_name != ability.name and any(a.name == new_name for a in self.abilities):
                    messagebox.showwarning("警告", "该能力标签已存在！")
                    return

                # 检查是否形成循环引用
                def has_cycle(current_name, target_name):
                    while current_name:
                        if current_name == target_name:
                            return True
                        current_ability = next((a for a in self.abilities if a.name == current_name), None)
                        if current_ability:
                            current_name = current_ability.parent
                        else:
                            break
                    return False

                if has_cycle(new_parent, ability.name):
                    messagebox.showwarning("警告", "不能将子能力设置为父能力！")
                    return

                # 更新能力标签
                ability.name = new_name
                ability.parent = new_parent

                self.data_manager.save_abilities(self.abilities)
                self.refresh_treeview()
                edit_window.destroy()
                display_info("成功", "能力标签已更新。")

            save_button = tk.Button(edit_window, text="保存修改", command=save_changes)
            save_button.grid(row=2, column=0, columnspan=2, pady=10)
        else:
            messagebox.showwarning("警告", "请选择要编辑的能力标签！")

    def delete_ability(self):
        """
        删除选中的能力标签。
        """
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            ability = next((a for a in self.abilities if a.name == selected_name), None)

            if not ability:
                messagebox.showwarning("警告", "未找到选中的能力标签！")
                return

            # 检查是否有其他标签以当前标签为父标签
            children = [a for a in self.abilities if a.parent == ability.name]
            if children:
                messagebox.showwarning("警告", f"无法删除 '{ability.name}' 标签，因为它有子标签。")
                return

            confirm = messagebox.askyesno("确认", f"确定要删除能力标签 '{ability.name}' 吗？")
            if confirm:
                self.abilities.remove(ability)
                self.data_manager.save_abilities(self.abilities)
                self.refresh_treeview()
                display_info("成功", "能力标签已删除。")
        else:
            messagebox.showwarning("警告", "请选择要删除的能力标签！")

    def visualize_abilities(self):
        """
        使用 networkx 和 matplotlib 绘制能力树
        """
        # 导入必要的库
        import networkx as nx
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.font_manager as fms

        # 设置中文字体
        plt.rcParams['font.family'] = 'SimHei'  # 替换为您的中文字体名称
        plt.rcParams['axes.unicode_minus'] = False

        # 创建有向图
        G = nx.DiGraph()

        # 添加节点和边
        for ability in self.abilities:
            G.add_node(ability.name)
            if ability.parent:
                G.add_edge(ability.parent, ability.name)

        # 绘制图形
        fig = plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            font_family='SimHei',  # 指定字体
            node_color='lightblue',
            edge_color='gray',
            node_size=2000,
            arrows=True,
            arrowsize=20
        )

        # 将绘制的图形嵌入到 Tkinter 窗口中
        self.show_graph_image(fig)


    def show_graph_image(self, fig):
        """
        在 Tkinter 窗口中显示 matplotlib 图形
        """
        image_window = tk.Toplevel(self.parent)
        image_window.title("能力树图形展示")
        image_window.grab_set()

        # 在 Tkinter 窗口中嵌入 matplotlib 图形
        canvas = FigureCanvasTkAgg(fig, master=image_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        def on_close():
            plt.close(fig)
            image_window.destroy()

        close_button = tk.Button(image_window, text="关闭", command=on_close)
        close_button.pack(pady=10)
