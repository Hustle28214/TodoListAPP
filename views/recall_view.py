# recall_view.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import random
from models import AbilityTag, KnowledgePoint
from data_manager import DataManager

class RecallView:
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.abilities = self.data_manager.load_abilities()
        self.projects = self.data_manager.load_projects()
        
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)
        
        self.create_widgets()
        self.load_recall_data()
    
    def create_widgets(self):
        label = tk.Label(self.frame, text="知识点回忆", font=("Microsoft YaHei", 16))
        label.pack(pady=10)
        
        # 回忆知识点区域
        recall_frame = ttk.LabelFrame(self.frame, text="需要回忆的知识点")
        recall_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.recall_listbox = tk.Listbox(recall_frame, width=100, height=10)
        self.recall_listbox.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10), pady=5)
        
        recall_scrollbar = ttk.Scrollbar(recall_frame, orient="vertical", command=self.recall_listbox.yview)
        recall_scrollbar.pack(side=tk.LEFT, fill='y')
        self.recall_listbox.config(yscrollcommand=recall_scrollbar.set)
        
        recall_buttons_frame = tk.Frame(recall_frame)
        recall_buttons_frame.pack(side=tk.LEFT, fill='y', pady=5)
        
        mark_recalled_button = tk.Button(recall_buttons_frame, text="标记为已回忆", command=self.mark_as_recalled)
        mark_recalled_button.pack(pady=5)
        
        add_ability_button_recall = tk.Button(recall_buttons_frame, text="添加能力标签", command=lambda: self.add_ability_tag(recall_frame))
        add_ability_button_recall.pack(pady=5)
        
        # 绑定双击事件以查看知识点详情
        self.recall_listbox.bind("<Double-1>", self.on_double_click_recall)
        
        # 未学习的知识点区域
        unlearned_frame = ttk.LabelFrame(self.frame, text="未学习的知识点（每日随机6个）")
        unlearned_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.unlearned_listbox = tk.Listbox(unlearned_frame, width=100, height=10)
        self.unlearned_listbox.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10), pady=5)
        
        unlearned_scrollbar = ttk.Scrollbar(unlearned_frame, orient="vertical", command=self.unlearned_listbox.yview)
        unlearned_scrollbar.pack(side=tk.LEFT, fill='y')
        self.unlearned_listbox.config(yscrollcommand=unlearned_scrollbar.set)
        
        unlearned_buttons_frame = tk.Frame(unlearned_frame)
        unlearned_buttons_frame.pack(side=tk.LEFT, fill='y', pady=5)
        
        start_learning_button = tk.Button(unlearned_buttons_frame, text="开始学习", command=self.start_learning)
        start_learning_button.pack(pady=5)
        
        change_batch_button = tk.Button(unlearned_buttons_frame, text="换一批", command=self.change_batch)
        change_batch_button.pack(pady=5)
        
        # add_ability_button_unlearned = tk.Button(unlearned_buttons_frame, text="添加能力标签", command=lambda: self.add_ability_tag(unlearned_frame))
        # add_ability_button_unlearned.pack(pady=5)
        
        # 绑定双击事件以查看未学习知识点详情（可选）
        self.unlearned_listbox.bind("<Double-1>", self.on_double_click_unlearned)
    
    def load_recall_data(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        self.due_recall_kps = []
        self.unlearned_kps = []
        
        # 遍历所有能力标签和知识点
        for ability in self.abilities:
            for kp in ability.knowledge_points:
                if kp.learned and kp.next_recall:
                    if kp.next_recall <= today_str:
                        self.due_recall_kps.append((ability.name, kp))
                elif not kp.learned:
                    self.unlearned_kps.append(kp)
        
        # 展示需要回忆的知识点
        self.recall_listbox.delete(0, tk.END)
        for ability_name, kp in self.due_recall_kps:
            last_recall = kp.last_recall if kp.last_recall else "无"
            next_recall = kp.next_recall if kp.next_recall else "无"
            self.recall_listbox.insert(tk.END, f"能力标签: {ability_name} | 知识点: {kp.content} | 上次回忆: {last_recall} | 下次回忆: {next_recall}")
        
        # 随机选择6个未学习的知识点
        random.shuffle(self.unlearned_kps)
        self.today_unlearned_kps = self.unlearned_kps[:6]
        
        # 展示未学习的知识点
        self.unlearned_listbox.delete(0, tk.END)
        for kp in self.today_unlearned_kps:
            self.unlearned_listbox.insert(tk.END, f"知识点: {kp.content}")
    
    def mark_as_recalled(self):
        selected_indices = self.recall_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请选择要标记为已回忆的知识点。")
            return
        
        index = selected_indices[0]
        ability_name, kp = self.due_recall_kps[index]
        
        # 更新知识点的 last_recall 和 next_recall
        today = datetime.now().date()
        kp.last_recall = today.strftime('%Y-%m-%d')
        kp.next_recall = self.calculate_next_recall_date(today, kp).strftime('%Y-%m-%d')
        
        # 保存数据
        self.data_manager.save_abilities(self.abilities)
        
        messagebox.showinfo("成功", f"知识点 '{kp.content}' 已标记为已回忆。")
        
        # 重新加载数据
        self.load_recall_data()
    
    def start_learning(self):
        selected_indices = self.unlearned_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请选择要开始学习的知识点。")
            return
        
        for index in selected_indices:
            kp = self.today_unlearned_kps[index]
            kp.learned = True
            today = datetime.now().date()
            kp.last_recall = today.strftime('%Y-%m-%d')
            kp.next_recall = (today + timedelta(days=1)).strftime('%Y-%m-%d')  # 初始回忆设为1天后
        
        # 保存数据
        self.data_manager.save_abilities(self.abilities)
        
        messagebox.showinfo("成功", "选定的知识点已标记为已学习。")
        
        # 重新加载数据
        self.load_recall_data()
    
    def change_batch(self):
        """
        换一批新的未学习知识点。
        """
        if not self.unlearned_kps:
            messagebox.showinfo("提示", "没有更多的未学习知识点可供选择。")
            return
        
        random.shuffle(self.unlearned_kps)
        self.today_unlearned_kps = self.unlearned_kps[:6]
        
        # 展示未学习的知识点
        self.unlearned_listbox.delete(0, tk.END)
        for kp in self.today_unlearned_kps:
            self.unlearned_listbox.insert(tk.END, f"知识点: {kp.content}")
    
    def calculate_next_recall_date(self, last_recall_date, kp):
        """
        根据艾宾浩斯遗忘曲线计算下次回忆的日期。
        简单的间隔列表，用户每次回忆成功后，下次回忆间隔翻倍。
        """
        # 定义回忆间隔（天）
        intervals = [1, 2, 4, 7, 15, 30, 60, 90]
        
        # 计算已经回忆的次数
        if not kp.last_recall:
            count = 0
        else:
            # 从 kp.last_recall 到 now，计算已经回忆了几次
            count = 0
            # 假设每次回忆成功后，间隔翻倍
            # 实际应用中可能需要更复杂的逻辑
            last_recall_date_obj = datetime.strptime(kp.last_recall, '%Y-%m-%d').date()
            days_since_last = (last_recall_date - last_recall_date_obj).days
            for interval in intervals:
                if days_since_last >= interval:
                    count += 1
                else:
                    break
        
        # 选择下一个回忆间隔
        if count < len(intervals):
            next_interval = intervals[count]
        else:
            next_interval = intervals[-1]  # 最长间隔
        
        return last_recall_date + timedelta(days=next_interval)
    
    def on_double_click_recall(self, event):
        selected_indices = self.recall_listbox.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        ability_name, kp = self.due_recall_kps[index]
        self.open_kp_details_window(ability_name, kp)
    
    def on_double_click_unlearned(self, event):
        selected_indices = self.unlearned_listbox.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        kp = self.today_unlearned_kps[index]
        # 找到知识点所属的能力标签
        ability_name = self.find_ability_of_kp(kp)
        if ability_name:
            self.open_kp_details_window(ability_name, kp)
        else:
            messagebox.showerror("错误", f"无法找到知识点 '{kp.content}' 的所属能力标签。")
    
    def find_ability_of_kp(self, kp):
        for ability in self.abilities:
            if kp in ability.knowledge_points:
                return ability.name
        return None
    
    def open_kp_details_window(self, ability_name, kp):
        """
        打开一个窗口，显示知识点的详细信息，包括能力标签链。
        """
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"知识点详情 - {kp.content}")
        details_window.geometry("400x300")
        details_window.grab_set()  # 模态窗口
        
        # 知识点信息
        info_frame = ttk.Frame(details_window, padding=10)
        info_frame.pack(fill='both', expand=True)
        
        tk.Label(info_frame, text=f"知识点: {kp.content}", font=("Microsoft YaHei", 12, "bold")).pack(anchor='w', pady=5)
        tk.Label(info_frame, text=f"所属能力标签: {ability_name}", font=("Microsoft YaHei", 11)).pack(anchor='w', pady=5)
        last_recall = kp.last_recall if kp.last_recall else "无"
        next_recall = kp.next_recall if kp.next_recall else "无"
        tk.Label(info_frame, text=f"上次回忆: {last_recall}", font=("Microsoft YaHei", 11)).pack(anchor='w', pady=5)
        tk.Label(info_frame, text=f"下次回忆: {next_recall}", font=("Microsoft YaHei", 11)).pack(anchor='w', pady=5)
        
        # 能力标签链
        chain = self.get_ability_chain(ability_name)
        chain_str = " -> ".join(chain) if chain else "无"
        tk.Label(info_frame, text=f"能力标签链: {chain_str}", font=("Microsoft YaHei", 11)).pack(anchor='w', pady=5)
        
        # 关闭按钮
        close_button = tk.Button(details_window, text="关闭", command=details_window.destroy)
        close_button.pack(pady=10)
    
    def get_ability_chain(self, ability_name):
        """
        获取能力标签的链，从当前能力标签到根能力标签。
        """
        chain = []
        current_name = ability_name
        while current_name:
            chain.append(current_name)
            ability = next((a for a in self.abilities if a.name == current_name), None)
            if ability and ability.parent:
                current_name = ability.parent
            else:
                current_name = None
        return chain[::-1]  # 从根到当前能力标签
    
    def add_ability_tag(self, parent_window):
        """
        添加新的能力标签。
        
        :param parent_window: 父窗口，用于定位对话框
        """
        new_tag = simpledialog.askstring("添加能力标签", "请输入新的能力标签:", parent=parent_window)
        if new_tag:
            if any(ability.name == new_tag for ability in self.abilities):
                messagebox.showinfo("提示", "该能力标签已存在。")
            else:
                # 选择父能力标签（可选）
                parent_options = ["无"] + [ability.name for ability in self.abilities if ability.parent is None]
                parent_selected = self.select_parent_ability(parent_window, parent_options)
                
                if parent_selected is None:
                    # 用户取消了选择
                    return
                
                if parent_selected == "无":
                    parent_selected = None
                
                new_ability = AbilityTag(name=new_tag, parent=parent_selected)
                self.abilities.append(new_ability)
                self.data_manager.save_abilities(self.abilities)
                messagebox.showinfo("成功", "能力标签已添加。")
                
                # 更新列表框中的能力标签
                children = parent_window.winfo_children()
                for widget in children:
                    if isinstance(widget, tk.Listbox):
                        abilities_var = tk.Variable(value=[ability.name for ability in self.abilities])
                        widget.config(listvariable=abilities_var)
                        break
    
    def select_parent_ability(self, parent_window, options):
        """
        弹出一个对话框，让用户选择父能力标签。
        
        :param parent_window: 父窗口
        :param options: 可供选择的父能力标签列表
        :return: 选择的父能力标签名称或 None
        """
        selection_window = tk.Toplevel(parent_window)
        selection_window.title("选择父能力标签")
        selection_window.grab_set()  # 模态窗口
        
        tk.Label(selection_window, text="请选择父能力标签（可选）:").pack(padx=10, pady=10)
        
        selected_parent = tk.StringVar(value="无")
        combobox = ttk.Combobox(selection_window, textvariable=selected_parent, values=options, state='readonly')
        combobox.pack(padx=10, pady=5)
        combobox.current(0)  # 默认选择“无”
        
        def confirm_selection():
            selection_window.destroy()
        
        confirm_button = tk.Button(selection_window, text="确认", command=confirm_selection)
        confirm_button.pack(pady=10)
        
        self.parent.wait_window(selection_window)
        
        if selected_parent.get() == "无":
            return None
        else:
            return selected_parent.get()
