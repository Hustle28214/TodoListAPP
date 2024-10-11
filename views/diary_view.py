# views/diary_view.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import Calendar
from models import DiaryEntry, AbilityTag
from utils import display_error, display_info
from datetime import datetime, date
import webbrowser

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
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        # 使用自定义样式的按钮
        style = ttk.Style()
        style.configure("Rounded.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=10,
                        relief="flat",
                        background="#4CAF50",
                        foreground="white")
        style.map("Rounded.TButton",
                  background=[("active", "#388E3C")])

        # 添加日记按钮
        add_diary_button = ttk.Button(buttons_frame, text="添加日记", command=self.open_add_diary_window, style="Rounded.TButton")
        add_diary_button.pack(side=tk.LEFT, padx=5)
        # 添加工具提示
        self.create_tooltip(add_diary_button, "添加新的日记条目")

        # 查看日记按钮
        view_diary_button = ttk.Button(buttons_frame, text="查看日记", command=self.view_diary, style="Rounded.TButton")
        view_diary_button.pack(side=tk.LEFT, padx=5)
        # 添加工具提示
        self.create_tooltip(view_diary_button, "查看选定日期的日记条目")

        # 日历控件
        self.diary_calendar = Calendar(self.frame, selectmode='day', date_pattern='yyyy-mm-dd',
                                      font=("Microsoft YaHei", 10),
                                      headers_background="#4CAF50",
                                      headers_foreground="white",
                                      normalbackground="#f5f5f5",
                                      normalforeground="black",
                                      selectbackground="#4CAF50",
                                      selectforeground="white")
        self.diary_calendar.pack(padx=10, pady=10)
        self.diary_calendar.bind("<<CalendarSelected>>", self.on_diary_date_selected)

        self.mark_diary_dates()

    def create_tooltip(self, widget, text):
        """
        创建一个简单的工具提示。
        """
        tooltip = Tooltip(widget, text)

    def mark_diary_dates(self):
        """
        在日历上标记有日记的日期。
        使用不同颜色或图标区分不同类型的日记。
        """
        self.diary_calendar.calevent_remove('all')
        for entry in self.diary_entries:
            entry_date = entry.entry_date  # 已经是 datetime.date 对象
            # 使用不同的颜色根据分类标签
            color = "#FF6347"  # 默认为番茄红
            if entry.category == "感兴趣的技术":
                color = "#1E90FF"  # 道奇蓝
            elif entry.category == "课外课程":
                color = "#32CD32"  # 石灰绿
            self.diary_calendar.calevent_create(entry_date, 'diary', 'circle')
            self.diary_calendar.tag_config('diary', background=color, foreground='white', font=("Microsoft YaHei", 10, "bold"))

    def open_add_diary_window(self):
        """
        打开添加日记的窗口。
        """
        add_diary_window = tk.Toplevel(self.parent)
        add_diary_window.title("添加日记")
        add_diary_window.geometry("500x600")
        add_diary_window.grab_set()  # 模态窗口

        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        # 使用 Notebook 分隔日记内容和标签
        notebook = ttk.Notebook(add_diary_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 日记内容页
        content_frame = ttk.Frame(notebook)
        notebook.add(content_frame, text="内容")

        ttk.Label(content_frame, text=f"日期: {selected_date.strftime('%Y-%m-%d')}", font=("Microsoft YaHei", 12, "bold")).pack(pady=10)

        ttk.Label(content_frame, text="日记内容:", font=("Microsoft YaHei", 10)).pack(anchor='w', padx=10)
        summary_text = tk.Text(content_frame, width=50, height=10, font=("Microsoft YaHei", 10))
        summary_text.pack(padx=10, pady=5)

        # 分类标签页
        category_frame = ttk.Frame(notebook)
        notebook.add(category_frame, text="分类和标签")

        ttk.Label(category_frame, text="分类标签:", font=("Microsoft YaHei", 10)).pack(anchor='w', padx=10, pady=5)
        category_var = tk.StringVar()
        category_combobox = ttk.Combobox(category_frame, textvariable=category_var, 
                                        values=["课内课程", "课外课程", "感兴趣的技术"], state='readonly', font=("Microsoft YaHei", 10))
        category_combobox.pack(padx=10, pady=5)
        category_combobox.set("课内课程")

        # 自定义标签
        ttk.Label(category_frame, text="自定义标签:", font=("Microsoft YaHei", 10)).pack(anchor='w', padx=10, pady=5)
        custom_tag_entry = tk.Entry(category_frame, width=50, font=("Microsoft YaHei", 10))
        custom_tag_entry.pack(padx=10, pady=5)

        # 关联能力标签
        ttk.Label(category_frame, text="关联能力标签:", font=("Microsoft YaHei", 10)).pack(anchor='w', padx=10, pady=5)
        abilities_listbox = tk.Listbox(category_frame, selectmode='multiple', font=("Microsoft YaHei", 10), width=50, height=5)
        abilities_listbox.pack(padx=10, pady=5)
        for ability in self.abilities:
            abilities_listbox.insert(tk.END, ability.name)

        # 链接输入框（仅在“感兴趣的技术”选项下显示）
        links_frame = ttk.Frame(category_frame)
        links_frame.pack(padx=10, pady=5, fill='x')
        links_label = ttk.Label(links_frame, text="相关链接 (最多4个):", font=("Microsoft YaHei", 10))
        links_label.pack(anchor='w')
        link_entries = []
        for i in range(4):
            entry = ttk.Entry(links_frame, width=50, font=("Microsoft YaHei", 10))
            entry.pack(anchor='w', pady=2)
            link_entries.append(entry)

        # 根据选择的分类标签，显示不同的输入选项
        def on_category_change(event):
            selected = category_var.get()
            if selected == "感兴趣的技术":
                links_label.pack(anchor='w')
                for entry in link_entries:
                    entry.pack(anchor='w', pady=2)
            else:
                links_label.pack_forget()
                for entry in link_entries:
                    entry.pack_forget()

        category_combobox.bind("<<ComboboxSelected>>", on_category_change)

        # 保存按钮
        save_button = ttk.Button(add_diary_window, text="添加", command=lambda: self.add_diary(add_diary_window, summary_text, category_var, custom_tag_entry, abilities_listbox, link_entries), style="Rounded.TButton")
        save_button.pack(pady=10)

    def add_diary(self, window, summary_text, category_var, custom_tag_entry, abilities_listbox, link_entries):
        summary = summary_text.get("1.0", tk.END).strip()
        category = category_var.get()
        custom_tag = custom_tag_entry.get().strip()
        selected_indices = abilities_listbox.curselection()
        selected_tags = [self.abilities[idx] for idx in selected_indices]
        links = [entry.get().strip() for entry in link_entries if entry.get().strip()]

        if not summary:
            messagebox.showwarning("警告", "日记内容不能为空！")
            return

        # 检查是否已存在该日期的日记
        for entry in self.diary_entries:
            if entry.entry_date == self.diary_calendar.get_date():
                display_error("警告", "该日期的日记已存在！")
                return

        # 处理自定义标签
        tags = selected_tags.copy()
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
            entry_date=self.diary_calendar.get_date(),
            summary=summary,
            category=category,
            tags=tags,  # 使用 tags 参数
            links=links
        )
        self.diary_entries.append(new_entry)
        self.data_manager.save_diary_entries(self.diary_entries)
        self.mark_diary_dates()
        window.destroy()
        display_info("成功", "日记已添加。")

    def on_diary_date_selected(self, event):
        """
        当选择日历中的日期时，查看该日期的日记。
        """
        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        for entry in self.diary_entries:
            if entry.entry_date == selected_date:
                self.open_view_diary_window(entry)
                return
        messagebox.showinfo("提示", "该日期暂无日记。")

    def view_diary(self):
        """
        查看选中日期的日记。
        """
        selected_date_str = self.diary_calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        for entry in self.diary_entries:
            if entry.entry_date == selected_date:
                self.open_view_diary_window(entry)
                return
        messagebox.showinfo("提示", "该日期暂无日记。")

    def open_view_diary_window(self, entry):
        """
        打开查看日记的窗口。
        """
        view_window = tk.Toplevel(self.parent)
        view_window.title(f"{entry.entry_date} 的日记")
        view_window.geometry("600x600")
        view_window.grab_set()  # 模态窗口

        # 使用 Notebook 分隔内容
        notebook = ttk.Notebook(view_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 日记内容页
        content_frame = ttk.Frame(notebook)
        notebook.add(content_frame, text="内容")

        ttk.Label(content_frame, text=f"日期: {entry.entry_date}", font=("Microsoft YaHei", 12, "bold")).pack(pady=10)

        ttk.Label(content_frame, text=f"分类标签: {entry.category}", font=("Microsoft YaHei", 10, "italic")).pack(pady=5, anchor='w', padx=10)

        if entry.tags:
            tags_str = ", ".join([tag.name for tag in entry.tags])
            ttk.Label(content_frame, text=f"标签: {tags_str}", font=("Microsoft YaHei", 10)).pack(pady=5, anchor='w', padx=10)

        ttk.Label(content_frame, text="日记内容:", font=("Microsoft YaHei", 10)).pack(anchor='w', padx=10, pady=5)
        summary_text = tk.Text(content_frame, width=60, height=15, font=("Microsoft YaHei", 10))
        summary_text.pack(padx=10, pady=5)
        summary_text.insert("1.0", entry.summary)
        summary_text.config(state='disabled')  # 只读

        # 关联链接页
        if entry.category == "感兴趣的技术" and entry.links:
            links_frame = ttk.Frame(notebook)
            notebook.add(links_frame, text="相关链接")

            ttk.Label(links_frame, text="相关链接:", font=("Microsoft YaHei", 10, "bold")).pack(pady=10, anchor='w', padx=10)

            for link in entry.links:
                link_label = ttk.Label(links_frame, text=link, foreground="blue", cursor="hand2", font=("Microsoft YaHei", 10, "underline"))
                link_label.pack(anchor='w', padx=20)
                link_label.bind("<Button-1>", lambda e, url=link: self.open_link(url))

        # 关闭按钮
        close_button = ttk.Button(view_window, text="关闭", command=view_window.destroy, style="Rounded.TButton")
        close_button.pack(pady=10)

    def open_link(self, url):
        """
        打开链接。
        """
        webbrowser.open(url)

# 工具提示类
class Tooltip:
    """
    创建一个工具提示类。
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # 无边框
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Microsoft YaHei", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
