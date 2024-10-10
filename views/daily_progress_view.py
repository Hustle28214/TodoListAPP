# views/daily_progress_view.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import Calendar
from models import DailyProgress, AbilityTag
from utils import display_error, display_info
from datetime import datetime

class DailyProgressView:
    def __init__(self, parent, data_manager, abilities):
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities  # List of AbilityTag objects
        self.daily_progress_list = self.data_manager.load_daily_progress()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()
        self.refresh_treeview()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_note_button = tk.Button(buttons_frame, text="添加/编辑备注", command=self.add_edit_note)
        add_note_button.pack(side=tk.LEFT, padx=5)

        # Treeview（每日进度列表）
        columns = ("Date", "Tasks Completed", "Notes", "Tags")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Notes":
                self.tree.column(col, width=300)
            else:
                self.tree.column(col, width=150)

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_treeview(self):
        # 同步每日进度
        self.data_manager.synchronize_daily_progress()
        self.daily_progress_list = self.data_manager.load_daily_progress()

        # 清空现有的树视图内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 按日期排序
        sorted_progress = sorted(self.daily_progress_list, key=lambda dp: dp.progress_date, reverse=True)
        for entry in sorted_progress:
            tags_str = ", ".join([tag.name for tag in entry.tags]) if entry.tags else "无"
            notes_preview = entry.notes if entry.notes else "无"
            self.tree.insert('', tk.END, values=(
                entry.progress_date,
                entry.tasks_completed,
                notes_preview,
                tags_str
            ))

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

