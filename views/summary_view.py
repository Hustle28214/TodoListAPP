# views/summary_view.py
import tkinter as tk
from tkinter import messagebox, ttk
from models import PeriodicSummary
from utils import display_error, display_info
from tkcalendar import Calendar

class SummaryView:
    def __init__(self, parent, data_manager):
        """
        初始化阶段性总结视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        """
        self.parent = parent
        self.data_manager = data_manager
        self.summaries = self.data_manager.load_summaries()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_summary_button = tk.Button(buttons_frame, text="添加总结", command=self.open_add_summary_window)
        add_summary_button.pack(side=tk.LEFT, padx=5)

        view_summary_button = tk.Button(buttons_frame, text="查看总结", command=self.view_summary)
        view_summary_button.pack(side=tk.LEFT, padx=5)

        delete_summary_button = tk.Button(buttons_frame, text="删除总结", command=self.delete_summary)
        delete_summary_button.pack(side=tk.LEFT, padx=5)

        # Treeview（总结列表）
        columns = ("Title", "Summary Date", "Content")
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', selectmode='browse')

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Content":
                self.tree.column(col, width=300)
            else:
                self.tree.column(col, width=150)

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_treeview()

    def refresh_treeview(self):
        """
        刷新总结列表的Treeview。
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for summary in self.summaries:
            self.tree.insert('', tk.END, values=(
                summary.title,
                summary.summary_date,
                summary.content
            ))

    def open_add_summary_window(self):
        """
        打开添加总结的窗口。
        """
        add_summary_window = tk.Toplevel(self.parent)
        add_summary_window.title("添加阶段性总结")
        add_summary_window.grab_set()  # 模态窗口

        # 标题
        tk.Label(add_summary_window, text="总结标题:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        title_entry = tk.Entry(add_summary_window, width=50)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        # 总结日期
        tk.Label(add_summary_window, text="总结日期:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        cal = Calendar(add_summary_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.grid(row=1, column=1, padx=10, pady=5)

        # 内容
        tk.Label(add_summary_window, text="总结内容:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.NW)
        content_text = tk.Text(add_summary_window, width=50, height=10)
        content_text.grid(row=2, column=1, padx=10, pady=5)

        # 添加按钮
        def add_summary():
            title = title_entry.get().strip()
            summary_date = cal.get_date()
            content = content_text.get("1.0", tk.END).strip()

            if not title:
                messagebox.showwarning("警告", "总结标题不能为空！")
                return
            if not content:
                messagebox.showwarning("警告", "总结内容不能为空！")
                return

            new_summary = PeriodicSummary(title, content, summary_date)
            self.summaries.append(new_summary)
            self.data_manager.save_summaries(self.summaries)
            self.refresh_treeview()
            add_summary_window.destroy()
            display_info("成功", "阶段性总结已添加。")

        add_button = tk.Button(add_summary_window, text="添加", command=add_summary)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

    def view_summary(self):
        """
        查看选中的总结。
        """
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            summary = self.summaries[index]

            view_window = tk.Toplevel(self.parent)
            view_window.title(f"总结: {summary.title}")
            view_window.grab_set()  # 模态窗口

            tk.Label(view_window, text=f"标题: {summary.title}", font=('Arial', 14, 'bold')).pack(padx=10, pady=5)
            tk.Label(view_window, text=f"总结日期: {summary.summary_date}", font=('Arial', 12)).pack(padx=10, pady=5)

            content_text = tk.Text(view_window, width=60, height=15)
            content_text.pack(padx=10, pady=5)
            content_text.insert("1.0", summary.content)
            content_text.config(state='disabled')  # 只读

            close_button = tk.Button(view_window, text="关闭", command=view_window.destroy)
            close_button.pack(pady=10)
        else:
            messagebox.showwarning("警告", "请选择要查看的总结！")

    def delete_summary(self):
        """
        删除选中的总结。
        """
        selected_item = self.tree.selection()
        if selected_item:
            confirm = messagebox.askyesno("确认", "确定要删除选中的总结吗？")
            if confirm:
                index = self.tree.index(selected_item)
                del self.summaries[index]
                self.data_manager.save_summaries(self.summaries)
                self.refresh_treeview()
                display_info("成功", "总结已删除。")
        else:
            messagebox.showwarning("警告", "请选择要删除的总结！")
