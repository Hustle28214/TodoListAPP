# views/analysis_view.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import font_manager as fm

# 设置全局字体为 SimSun
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 你可以选择 SimHei, SimSun 或其他中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

class AnalysisView:
    def __init__(self, parent, data_manager, abilities):
        """
        初始化分析视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        :param abilities: 能力标签列表
        """
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities

        self.tasks = self.data_manager.load_tasks()
        self.projects = self.data_manager.load_projects()

        # 设置字体路径以显示中文
        font_path = 'C:/Windows/Fonts/simsun.ttc'  # 替换为系统中的中文字体路径
        self.my_font = fm.FontProperties(fname=font_path)

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        """
        创建分析界面组件。
        """
        label = tk.Label(self.frame, text="数据分析", font=("Microsoft YaHei", 16))
        label.pack(pady=10)

        # 分析按钮
        task_completion_button = tk.Button(self.frame, text="任务完成情况", command=self.show_task_completion_chart)
        task_completion_button.pack(pady=5)

        project_analysis_button = tk.Button(self.frame, text="按能力标签分析项目", command=self.show_project_analysis_chart)
        project_analysis_button.pack(pady=5)

    def show_task_completion_chart(self):
        """
        显示任务完成情况的饼图。
        """
        completed_tasks = len([t for t in self.tasks if t.progress == 100])
        uncompleted_tasks = len([t for t in self.tasks if t.progress < 100])

        if completed_tasks + uncompleted_tasks == 0:
            messagebox.showinfo("无数据", "没有任务数据可以分析。")
            return

        labels = ['已完成', '未完成']
        sizes = [completed_tasks, uncompleted_tasks]
        colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)  # 突出显示已完成任务

        fig, ax = plt.subplots()
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')  # 保证饼图为圆形

        # 设置标题，使用中文字体
        ax.set_title("任务完成情况", fontproperties=self.my_font)

        # 嵌入到Tkinter中
        self.display_chart_in_window(fig)

    def show_project_analysis_chart(self):
        """
        显示按能力标签分析项目的柱状图。
        """
        if not self.projects:
            messagebox.showinfo("无数据", "没有项目数据可以分析。")
            return

        ability_count = {}
        for project in self.projects:
            for ability in project.abilities:
                if ability.name not in ability_count:
                    ability_count[ability.name] = 0
                ability_count[ability.name] += 1

        if not ability_count:
            messagebox.showinfo("无数据", "没有能力标签数据可以分析。")
            return

        abilities = list(ability_count.keys())
        counts = list(ability_count.values())

        fig, ax = plt.subplots()
        ax.bar(abilities, counts, color='#66b3ff')

        ax.set_xlabel("能力标签", fontproperties=self.my_font)
        ax.set_ylabel("项目数量", fontproperties=self.my_font)
        ax.set_title("按能力标签分析项目", fontproperties=self.my_font)

        ax.set_xticks(range(len(abilities)))  # 先设定固定的刻度
        ax.set_xticklabels(abilities, fontproperties=self.my_font, rotation=45, ha="right")

        # 嵌入到Tkinter中
        self.display_chart_in_window(fig)

    def display_chart_in_window(self, fig):
        """
        在新窗口中显示嵌入的图表。
        """
        chart_window = tk.Toplevel(self.parent)
        chart_window.title("分析结果")
        chart_window.geometry("600x400")

        # 创建绘图区域
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def on_close():
            plt.close(fig)
            chart_window.destroy()

        close_button = tk.Button(chart_window, text="关闭", command=on_close)
        close_button.pack(pady=10)
