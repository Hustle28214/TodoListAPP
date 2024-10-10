# views/diary_view.py
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import Calendar
from models import DiaryEntry, AbilityTag
from utils import display_error, display_info
from datetime import datetime

class DiaryView:
    def __init__(self, parent, data_manager, abilities):
        """
        初始化日记视图。

        :param parent: 父容器
        :param data_manager: 数据管理器实例
        :param abilities: 可用的能力标签列表
        """
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = abilities  # List of AbilityTag objects
        self.diary_entries = self.data_manager.load_diary_entries()

        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        # 按钮框架
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        add_diary_button = tk.Button(buttons_frame, text="添加日记", command=self.open_add_diary_window)
        add_diary_button.pack(side=tk.LEFT, padx=5)

        view_diary_button = tk.Button(buttons_frame, text="查看日记", command=self.view_diary)
        view_diary_button.pack(side=tk.LEFT, padx=5)

        # 日历控件
        self.diary_calendar = Calendar(self.frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.diary_calendar.pack(padx=10, pady=10)

        self.diary_calendar.bind("<<CalendarSelected>>", self.on_diary_date_selected)

        self.mark_diary_dates()

    def mark_diary_dates(self):
        """
        在日历上标记有日记的日期。
        """
        self.diary_calendar.calevent_remove('all')
        for entry in self.diary_entries:
            entry_date = entry.entry_date  # 已经是 datetime.date 对象
            self.diary_calendar.calevent_create(entry_date, 'diary', 'circle')
        self.diary_calendar.tag_config('diary', background='red', foreground='white')

    def open_add_diary_window(self):
        """
        打开添加日记的窗口。
        """
        add_diary_window = tk.Toplevel(self.parent)
        add_diary_window.title("添加日记")
        add_diary_window.grab_set()  # 模态窗口

        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        # 显示选中的日期
        tk.Label(add_diary_window, text=f"日期: {selected_date.strftime('%Y-%m-%d')}").pack(padx=10, pady=5)

        # 日记内容
        tk.Label(add_diary_window, text="日记内容:").pack(padx=10, pady=5)
        summary_text = tk.Text(add_diary_window, width=50, height=10)
        summary_text.pack(padx=10, pady=5)

        # 分类标签
        tk.Label(add_diary_window, text="分类标签:").pack(padx=10, pady=5)
        category_var = tk.StringVar()
        category_combobox = ttk.Combobox(add_diary_window, textvariable=category_var, values=["课内课程", "课外课程", "感兴趣的技术"], state='readonly')
        category_combobox.pack(padx=10, pady=5)
        category_combobox.set("课内课程")

        # 根据选择的分类标签，显示不同的输入选项
        def on_category_change(event):
            selected = category_var.get()
            if selected == "感兴趣的技术":
                links_label.pack(padx=10, pady=5)
                for entry in link_entries:
                    entry.pack(padx=10, pady=2)
            else:
                links_label.pack_forget()
                for entry in link_entries:
                    entry.pack_forget()

        category_combobox.bind("<<ComboboxSelected>>", on_category_change)

        # 自定义标签
        tk.Label(add_diary_window, text="自定义标签:").pack(padx=10, pady=5)
        custom_tag_entry = tk.Entry(add_diary_window, width=50)
        custom_tag_entry.pack(padx=10, pady=5)

        # 链接输入框（仅在“感兴趣的技术”选项下显示）
        links_label = tk.Label(add_diary_window, text="相关链接 (最多4个):")
        link_entries = []
        for i in range(4):
            entry = tk.Entry(add_diary_window, width=50)
            link_entries.append(entry)

        def add_diary():
            summary = summary_text.get("1.0", tk.END).strip()
            category = category_var.get()
            custom_tag = custom_tag_entry.get().strip()
            links = [entry.get().strip() for entry in link_entries if entry.get().strip()]

            if not summary:
                messagebox.showwarning("警告", "日记内容不能为空！")
                return

            # 检查是否已存在该日期的日记
            for entry in self.diary_entries:
                if entry.entry_date == selected_date:
                    messagebox.showwarning("警告", "该日期的日记已存在！")
                    return

            # 处理标签
            tags = []
            if custom_tag:
                # 检查是否已有该标签
                existing_tag = next((tag for tag in self.abilities if tag.name == custom_tag), None)
                if not existing_tag:
                    # 创建新的 AbilityTag
                    new_tag = AbilityTag(name=custom_tag)
                    self.abilities.append(new_tag)
                    self.data_manager.save_abilities(self.abilities)
                    tags.append(new_tag)
                else:
                    tags.append(existing_tag)

            new_entry = DiaryEntry(
                entry_date=selected_date,
                summary=summary,
                category=category,
                tags=tags,  # 使用 tags 参数
                links=links
            )
            self.diary_entries.append(new_entry)
            self.data_manager.save_diary_entries(self.diary_entries)
            self.mark_diary_dates()
            add_diary_window.destroy()
            display_info("成功", "日记已添加。")

        add_button = tk.Button(add_diary_window, text="添加", command=add_diary)
        add_button.pack(pady=10)

    def on_diary_date_selected(self, event):
        """
        当选择日历中的日期时，查看该日期的日记。
        """
        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        for entry in self.diary_entries:
            if entry.entry_date == selected_date:
                view_window = tk.Toplevel(self.parent)
                view_window.title(f"{selected_date.strftime('%Y-%m-%d')} 的日记")
                view_window.grab_set()  # 模态窗口

                tk.Label(view_window, text=f"日期: {selected_date.strftime('%Y-%m-%d')}", font=('Arial', 14, 'bold')).pack(padx=10, pady=10)

                tk.Label(view_window, text=f"分类标签: {entry.category}", font=('Arial', 12, 'italic')).pack(padx=10, pady=5)

                if entry.tags:
                    tags_str = ", ".join([tag.name for tag in entry.tags])
                    tk.Label(view_window, text=f"标签: {tags_str}", font=('Arial', 12)).pack(padx=10, pady=5)

                summary_text = tk.Text(view_window, width=50, height=10)
                summary_text.pack(padx=10, pady=10)
                summary_text.insert("1.0", entry.summary)
                summary_text.config(state='disabled')  # 只读

                if entry.category == "感兴趣的技术" and entry.links:
                    links_frame = tk.Frame(view_window)
                    links_frame.pack(padx=10, pady=5)
                    tk.Label(links_frame, text="相关链接:").pack(anchor=tk.W)
                    for link in entry.links:
                        link_label = tk.Label(links_frame, text=link, fg="blue", cursor="hand2")
                        link_label.pack(anchor=tk.W)
                        link_label.bind("<Button-1>", lambda e, url=link: self.open_link(url))

                close_button = tk.Button(view_window, text="关闭", command=view_window.destroy)
                close_button.pack(pady=10)
                return
        messagebox.showinfo("提示", "该日期暂无日记。")

    def open_link(self, url):
        """
        打开链接。
        """
        import webbrowser
        webbrowser.open(url)

    def view_diary(self):
        """
        查看选中日期的日记。
        """
        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        for entry in self.diary_entries:
            if entry.entry_date == selected_date:
                # 与 `on_diary_date_selected` 方法类似
                self.on_diary_date_selected(None)
                return
        messagebox.showinfo("提示", "该日期暂无日记。")
