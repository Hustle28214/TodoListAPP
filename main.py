import tkinter as tk
from tkinter import ttk
from data_manager import DataManager
from views.tasks_view import TasksView
from views.diary_view import DiaryView
from views.summary_view import SummaryView
from views.abilities_view import AbilitiesView
from views.projects_view import ProjectsView
from views.daily_progress_view import DailyProgressView
from views.analysis_view import AnalysisView  # 导入 AnalysisView
from views.goals_view import GoalsView  # 导入 GoalsView
from views.recall_view import RecallView
from models import AbilityTag
from views.pomodoro_view import PomodoroView  # 导入 PomodoroView


def configure_styles():
    """配置全局样式"""
    style = ttk.Style()

    # 设置全局字体和背景，使用 Microsoft YaHei 以支持中英文显示
    style.configure(".", font=("Microsoft YaHei", 11), background="#f7f7f7", foreground="black")

    # 定义Notebook样式
    style.configure("TNotebook", background="#f7f7f7")
    style.configure("TNotebook.Tab", padding=[10, 5], font=("Microsoft YaHei", 12, "bold"))

    # 定义Tab标签页的激活样式
    style.map("TNotebook.Tab", background=[("selected", "#4caf50")])

    # 定义按钮样式
    style.configure("TButton", font=("Microsoft YaHei", 10), padding=6, background="#4caf50", foreground="white")
    style.map("TButton", background=[("active", "#388e3c"), ("pressed", "#2e7d32")])

    # 配置Label样式
    style.configure("TLabel", font=("Microsoft YaHei", 11), background="#f7f7f7", padding=5)

    # 配置Frame样式
    style.configure("TFrame", background="#f7f7f7")

    # 配置Entry样式
    style.configure("TEntry", padding=4)

    # 增加Entry点击效果
    style.map("TEntry", foreground=[("focus", "#333333")])


def main():
    # 初始化主窗口
    root = tk.Tk()
    root.title("上岸")
    root.geometry("1000x700")

    # 设置窗口图标
    try:
        root.iconbitmap('todo.ico')
    except Exception as e:
        print(f"无法加载图标文件: {e}")

    # 初始化数据管理器
    data_manager = DataManager()

    # 加载能力标签
    abilities = data_manager.load_abilities()

    # 配置全局样式
    configure_styles()

    # 标题栏
    header = tk.Frame(root, bg="#4caf50", height=50)
    header.pack(fill="x")
    header_label = tk.Label(header, text="上岸", font=("Microsoft YaHei", 16, "bold"), bg="#4caf50", fg="white")
    header_label.pack(pady=10)

    # 创建Notebook（标签页）
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # 创建“任务”标签页
    tasks_frame = ttk.Frame(notebook)
    notebook.add(tasks_frame, text='运筹')
    TasksView(tasks_frame, data_manager, abilities)

    # 创建“拱卒”标签页
    daily_progress_frame = ttk.Frame(notebook)
    notebook.add(daily_progress_frame, text='拱卒')
    DailyProgressView(daily_progress_frame, data_manager, abilities)

    # 创建“日记”标签页
    diary_frame = ttk.Frame(notebook)
    notebook.add(diary_frame, text='拾遗')
    DiaryView(diary_frame, data_manager, abilities)

    # 创建“阶段性总结”标签页
    summary_frame = ttk.Frame(notebook)
    notebook.add(summary_frame, text='回首')
    SummaryView(summary_frame, data_manager)

    # 创建“能力标签”标签页
    abilities_frame = ttk.Frame(notebook)
    notebook.add(abilities_frame, text='宝物')
    AbilitiesView(abilities_frame, data_manager)

    # 创建“回忆知识点”标签页
    recall_frame = ttk.Frame(notebook)
    notebook.add(recall_frame, text="峥嵘")
    RecallView(recall_frame,data_manager)

    # 创建“项目”标签页
    projects_frame = ttk.Frame(notebook)
    notebook.add(projects_frame, text='高楼')
    ProjectsView(projects_frame, data_manager, abilities)

    # 创建“目标”标签页
    goals_frame = ttk.Frame(notebook)
    notebook.add(goals_frame, text="插旗")
    GoalsView(goals_frame, data_manager)

    # 创建“数据分析”标签页
    analysis_frame = ttk.Frame(notebook)
    notebook.add(analysis_frame, text="鉴证")
    AnalysisView(analysis_frame, data_manager, abilities)

    # 创建“番茄钟”标签页
    pomodoro_frame = ttk.Frame(notebook)
    notebook.add(pomodoro_frame, text="心流")
    PomodoroView(pomodoro_frame)

    # 页脚
    footer = tk.Frame(root, bg="#4caf50", height=30)
    footer.pack(fill="x", side="bottom")
    footer_label = tk.Label(footer, text="© 2024 Leyan Cai", bg="#4caf50", fg="white", font=("Microsoft YaHei", 10))
    footer_label.pack(pady=5)

    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
