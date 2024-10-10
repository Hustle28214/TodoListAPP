# main.py
import tkinter as tk
from tkinter import ttk
from data_manager import DataManager
from views.tasks_view import TasksView
from views.diary_view import DiaryView
from views.summary_view import SummaryView
from views.abilities_view import AbilitiesView
from views.projects_view import ProjectsView
from models import AbilityTag

def main():
    # 初始化主窗口
    root = tk.Tk()
    root.title("上岸")
    root.geometry("1000x700")  # 调整窗口大小以适应更多内容

    # 设置窗口图标
    try:
        root.iconbitmap('todo.ico')
    except Exception as e:
        print(f"无法加载图标文件: {e}")


    # 初始化数据管理器
    data_manager = DataManager()

    # 加载能力标签
    abilities = data_manager.load_abilities()

    # 创建Notebook（标签页）
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # 创建“任务”标签页
    tasks_frame = ttk.Frame(notebook)
    notebook.add(tasks_frame, text='运筹')
    TasksView(tasks_frame, data_manager, abilities)

    # 创建“日拱一卒”标签页
    daily_progress_frame = ttk.Frame(notebook)
    notebook.add(daily_progress_frame, text='拱卒')
    # 假设 DailyProgressView 已经实现
    # DailyProgressView(daily_progress_frame, data_manager)

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

    # 创建“项目”标签页
    projects_frame = ttk.Frame(notebook)
    notebook.add(projects_frame, text='高楼')
    ProjectsView(projects_frame, data_manager, abilities)

    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()
