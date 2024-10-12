# views/abilities_view.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from models import AbilityTag, KnowledgePoint
from utils import display_error, display_info
from datetime import datetime, date
import networkx as nx
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.font_manager as fm
import plotly.graph_objects as go
from collections import defaultdict
import webbrowser
import tempfile
import os
import threading

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
        self.projects = self.data_manager.load_projects()

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

        # 绑定双击事件以查看知识点
        self.tree.bind("<Double-1>", self.on_double_click)

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

        # 定义一个函数，判断子孙节点是否有匹配搜索关键字的
        def has_matching_descendant(ability):
            children = [a for a in self.abilities if a.parent == ability.name]
            for child in children:
                if matches_search(child) or has_matching_descendant(child):
                    return True
            return False

        # 递归地添加子节点
        def add_children(parent_ability, parent_item):
            children = [ability for ability in self.abilities if ability.parent == parent_ability.name]
            for child in children:
                # 如果子节点或其子孙节点匹配搜索，则添加到树中
                if matches_search(child) or has_matching_descendant(child):
                    child_item = self.tree.insert(parent_item, 'end', text=child.name, values=(child.name,))
                    tree_items[child.name] = child_item
                    add_children(child, child_item)

        # 添加根节点及其子节点
        roots = [ability for ability in self.abilities if not ability.parent]
        for root in roots:
            # 如果根节点或其子孙节点匹配搜索，则添加到树中
            if matches_search(root) or has_matching_descendant(root):
                root_item = self.tree.insert('', 'end', text=root.name, values=(root.name,))
                tree_items[root.name] = root_item
                add_children(root, root_item)

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            ability = next((a for a in self.abilities if a.name == selected_name), None)
            if ability:
                self.open_knowledge_points_window(ability)

    def open_knowledge_points_window(self, ability):
        """
        打开一个窗口，显示并管理选定能力标签的知识点。
        使用复选框来直接修改学习状态。
        """
        kp_window = tk.Toplevel(self.parent)
        kp_window.title(f"{ability.name} 的知识点")
        kp_window.grab_set()

        # 知识点列表框
        kp_frame = ttk.Frame(kp_window)
        kp_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 使用 Canvas 和 Scrollbar 来支持大量知识点
        canvas = tk.Canvas(kp_frame)
        scrollbar = ttk.Scrollbar(kp_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建复选框列表
        self.kp_vars = []
        for kp in ability.knowledge_points:
            var = tk.BooleanVar(value=kp.learned)
            cb = tk.Checkbutton(scrollable_frame, text=kp.content, variable=var,
                                command=lambda kp=kp, var=var: self.update_kp_status(ability, kp, var))
            cb.pack(anchor='w', pady=2)
            self.kp_vars.append(var)

        # 按钮框架
        buttons_frame = tk.Frame(kp_window)
        buttons_frame.pack(pady=10)

        add_kp_button = tk.Button(buttons_frame, text="添加知识点", command=lambda: self.add_knowledge_point(ability, scrollable_frame))
        add_kp_button.pack(side=tk.LEFT, padx=5)

        delete_kp_button = tk.Button(buttons_frame, text="删除知识点", command=lambda: self.delete_knowledge_point(ability, scrollable_frame))
        delete_kp_button.pack(side=tk.LEFT, padx=5)

        # 显示相关项目
        projects_label = tk.Label(kp_window, text="相关项目:")
        projects_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        projects_list = tk.Listbox(kp_window, width=50)
        projects_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        related_projects = [p.name for p in self.projects if any(a.name == ability.name for a in p.abilities)]
        for project in related_projects:
            projects_list.insert(tk.END, project)

        # 关闭按钮
        close_button = tk.Button(kp_window, text="关闭", command=kp_window.destroy)
        close_button.pack(pady=10)

    def update_kp_status(self, ability, kp, var):
        """
        更新知识点的学习状态。
        """
        kp.learned = var.get()
        self.data_manager.save_abilities(self.abilities)

    def add_knowledge_point(self, ability, parent_frame):
        """
        添加新的知识点到能力标签。
        """
        content = simpledialog.askstring("添加知识点", "请输入知识点内容：", parent=self.parent)
        if content:
            new_kp = KnowledgePoint(content=content)
            ability.knowledge_points.append(new_kp)
            self.data_manager.save_abilities(self.abilities)
            # 添加新的复选框
            var = tk.BooleanVar(value=new_kp.learned)
            cb = tk.Checkbutton(parent_frame, text=new_kp.content, variable=var,
                                command=lambda kp=new_kp, var=var: self.update_kp_status(ability, kp, var))
            cb.pack(anchor='w', pady=2)
            self.kp_vars.append(var)
            display_info("成功", "知识点已添加。")

    def delete_knowledge_point(self, ability, parent_frame):
        """
        删除选定的知识点。
        """
        # 获取所有复选框的状态
        selected_indices = [idx for idx, var in enumerate(self.kp_vars) if var.get()]
        if not selected_indices:
            messagebox.showwarning("警告", "请选择要删除的知识点！")
            return

        confirm = messagebox.askyesno("确认", f"确定要删除选中的{len(selected_indices)}个知识点吗？")
        if confirm:
            # 删除从后向前，避免索引错乱
            for idx in sorted(selected_indices, reverse=True):
                if idx >= len(ability.knowledge_points):
                    continue  # 防止索引超出范围
                kp_to_delete = ability.knowledge_points[idx].content
                ability.knowledge_points.pop(idx)
                self.kp_vars.pop(idx)
                # 找到对应的复选框并销毁
                for child in parent_frame.winfo_children():
                    if isinstance(child, tk.Checkbutton) and child.cget("text") == kp_to_delete:
                        child.destroy()
                        break
            self.data_manager.save_abilities(self.abilities)
            display_info("成功", "选定的知识点已删除。")

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
                display_error("错误", "未找到选中的能力标签！")
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

                if new_parent and has_cycle(new_parent, ability.name):
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
            display_error("错误", "请选择要编辑的能力标签！")

    def delete_ability(self):
        """
        删除选中的能力标签。
        """
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            ability = next((a for a in self.abilities if a.name == selected_name), None)

            if not ability:
                display_error("错误", "未找到选中的能力标签！")
                return

            # 检查是否有其他标签以当前标签为父标签
            children = [a for a in self.abilities if a.parent == ability.name]
            if children:
                display_error("错误", f"无法删除 '{ability.name}' 标签，因为它有子标签。")
                return

            confirm = messagebox.askyesno("确认", f"确定要删除能力标签 '{ability.name}' 吗？")
            if confirm:
                self.abilities.remove(ability)
                self.data_manager.save_abilities(self.abilities)
                self.refresh_treeview()
                display_info("成功", "能力标签已删除。")
        else:
            display_error("错误", "请选择要删除的能力标签！")

    @staticmethod
    def create_dash_app(abilities, projects):
        """
        创建一个 Dash 应用，用于显示能力标签网络图。

        :param abilities: 能力标签列表
        :param projects: 项目列表
        :return: Dash 应用实例
        """
        import plotly.io as pio

        # 创建能力标签与项目的映射
        ability_projects = defaultdict(list)
        for project in projects:
            for ability in project.abilities:
                ability_projects[ability.name].append(project.name)

        # 创建有向图
        G = nx.DiGraph()
        for ability in abilities:
            if ability.name != "无":
                G.add_node(ability.name)
                if ability.parent and ability.parent != "无":
                    G.add_edge(ability.parent, ability.name)

        # 使用 Kamada-Kawai 布局生成节点位置
        pos = nx.kamada_kawai_layout(G, scale=2)

        # 提取布局的 x 和 y 坐标
        x_values = [pos[node][0] for node in G.nodes()]
        y_values = [pos[node][1] for node in G.nodes()]

        # 创建边的轨迹
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # 设置节点大小和颜色
        degrees = dict(G.degree())
        max_degree = max(degrees.values()) if degrees else 1
        node_size = [20 + 40 * (degrees[node] / max_degree) for node in G.nodes()]
        node_color = [degrees[node] for node in G.nodes()]

        # 创建边的 Plotly 轨迹
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # 准备节点的详细信息
        hover_text = []
        for node in G.nodes():
            projects = ability_projects.get(node, ["无"])
            ability_obj = next(a for a in abilities if a.name == node)
            knowledge_points = [kp.content for kp in ability_obj.knowledge_points]
            kp_text = " & ".join(knowledge_points) if knowledge_points else "无"
            projects_text = " & ".join(projects) if projects else "无"
            hover_text.append(f'能力标签: {node}<br>相关项目: {projects_text}<br>知识点: {kp_text}')

        # 创建节点的 Plotly 轨迹
        node_trace = go.Scatter(
            x=x_values, y=y_values,
            mode='markers+text',
            text=[node for node in G.nodes()],
            textposition='bottom center',
            hoverinfo='text',
            hovertext=hover_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                color=node_color,
                size=node_size,
                colorbar=dict(
                    thickness=15,
                    title='节点度数',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)
            )
        )

        # 创建布局
        layout = go.Layout(
            title='我的能力网',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )

        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

        # 初始化 Dash 应用
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Graph(
                id='ability-graph',
                figure=fig,
                style={'height': '60vh'}  # 设置图形高度为视口高度的60%
            ),
            html.Div(
                id='node-details',
                style={
                    'padding': '20px',
                    'border': '1px solid #ccc',
                    'max-height': '20vh',  # 设置详情部分的最大高度为视口高度的20%
                    'overflowY': 'auto'    # 添加垂直滚动条
                }
            )
        ])

        @app.callback(
            Output('node-details', 'children'),
            [Input('ability-graph', 'clickData')]
        )
        def display_click_data(clickData):
            if clickData is None:
                return "点击一个节点以查看详细信息。"
            else:
                point = clickData['points'][0]
                node_name = point['text']
                ability = next(a for a in abilities if a.name == node_name)
                projects = ability_projects.get(node_name, ["无"])
                knowledge_points = [kp.content for kp in ability.knowledge_points]
                kp_text = "<br>".join(knowledge_points) if knowledge_points else "无"
                projects_text = "<br>".join(projects) if projects else "无"
                return html.Div([
                    html.H4(f"能力标签: {node_name}"),
                    html.P(f"相关项目: {projects_text}"),
                    html.P(f"知识点: {kp_text}")
                ])

        return app

    # 在 visualize_abilities 方法中启动 Dash 应用
    def visualize_abilities(self):
        """
        启动 Dash 应用并自动在浏览器中打开。
        """
        app = self.create_dash_app(self.abilities, self.projects)
        
        # 定义服务器地址 可以后期再改
        server_url = "http://127.0.0.1:8050/" 

        # 启动 Dash 应用的函数
        def run_dash():
            app.run_server(port=8050, debug=False, use_reloader=False)

        # 启动 Dash 应用在新线程中
        threading.Thread(target=run_dash, daemon=True).start()

        # 等待 Dash 服务器启动
        import time
        time.sleep(1)  # 可以根据需要调整延迟时间

        # 自动打开浏览器
        webbrowser.open(server_url)

        display_info("提示", "能力标签网络图已在浏览器中打开。")

    def close_graph_window(self, fig, window):
        plt.close(fig)
        window.destroy()

    def show_ability_details(self, ability_name):
        """
        显示选定能力标签的相关项目和知识点。
        """
        ability = next((a for a in self.abilities if a.name == ability_name), None)
        if not ability:
            display_error("错误", f"未找到能力标签 '{ability_name}'")
            return

        details_window = tk.Toplevel(self.parent)
        details_window.title(f"{ability_name} 的详细信息")
        details_window.grab_set()

        # 项目列表
        projects = [p for p in self.projects if any(a.name == ability_name for a in p.abilities)]
        projects_label = tk.Label(details_window, text="相关项目:")
        projects_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        projects_list = tk.Listbox(details_window, width=50)
        projects_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for project in projects:
            projects_list.insert(tk.END, project.name)

        # 知识点列表
        kp_label = tk.Label(details_window, text="知识点:")
        kp_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        kp_list = ttk.Treeview(details_window, columns=('Learned'), show='headings')
        kp_list.heading('Learned', text='已学习')
        kp_list.column('Learned', width=100, anchor='center')
        kp_list.pack(fill='both', expand=True, padx=10, pady=5)

        for kp in ability.knowledge_points:
            kp_list.insert('', 'end', values=(kp.content, '✔️' if kp.learned else '❌'))

        # 关闭按钮
        close_button = tk.Button(details_window, text="关闭", command=details_window.destroy)
        close_button.pack(pady=10)
