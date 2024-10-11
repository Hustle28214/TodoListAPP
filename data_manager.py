# data_manager.py

import json
import os
from models import Task, DiaryEntry, PeriodicSummary, Project, AbilityTag, DailyProgress, Goal
from collections import defaultdict
import tempfile
import shutil

class DataManager:
    def __init__(self):
        # 定义数据文件路径
        self.tasks_file = "tasks.json"
        self.diary_file = "diary.json"
        self.summaries_file = "summaries.json"
        self.projects_file = "projects.json"
        self.abilities_file = "abilities.json"
        self.daily_progress_file = "daily_progress.json"
        self.goals_file = "goals.json"  # 添加目标文件路径

    # ----------------- 目标数据管理 ----------------- #
    def load_goals(self):
        """从 JSON 文件加载目标"""
        if os.path.exists(self.goals_file):
            try:
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Goal.from_dict(goal) for goal in data]
            except json.JSONDecodeError as e:
                print(f"加载目标时出错: {e}")
                return []
            except Exception as e:
                print(f"加载目标时出错: {e}")
                return []
        return []

    def save_goals(self, goals):
        """将目标保存到 JSON 文件"""
        try:
            data = [goal.to_dict() for goal in goals]
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存目标时出错: {e}")

    # ----------------- 任务数据管理 ----------------- #
    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Task.from_dict(task) for task in data]
            except json.JSONDecodeError as e:
                print(f"加载任务时出错: {e}")
                return []
            except Exception as e:
                print(f"加载任务时出错: {e}")
                return []
        return []

    def save_tasks(self, tasks):
        try:
            data = [task.to_dict() for task in tasks]
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存任务时出错: {e}")

    # ----------------- 每日进度（拱卒）数据管理 ----------------- #
    def load_daily_progress(self):
        if os.path.exists(self.daily_progress_file):
            try:
                with open(self.daily_progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [DailyProgress.from_dict(entry) for entry in data]
            except json.JSONDecodeError as e:
                print(f"加载每日进度时出错: {e}")
                return []
            except Exception as e:
                print(f"加载每日进度时出错: {e}")
                return []
        return []

    def save_daily_progress(self, daily_progress_list):
        try:
            data = [entry.to_dict() for entry in daily_progress_list]
            with open(self.daily_progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存每日进度时出错: {e}")

    # ----------------- 日记数据管理 ----------------- #
    def load_diary_entries(self):
        if os.path.exists(self.diary_file):
            try:
                with open(self.diary_file, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                    if not data:
                        return []
                    data = json.loads(data)
                    return [DiaryEntry.from_dict(entry) for entry in data]
            except json.JSONDecodeError as e:
                print(f"加载日记时出错: {e}")
                return []
            except Exception as e:
                print(f"加载日记时出错: {e}")
                return []
        return []

    def save_diary_entries(self, diary_entries):
        try:
            data = [entry.to_dict() for entry in diary_entries]
            with open(self.diary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存日记时出错: {e}")

    # ----------------- 阶段性总结数据管理 ----------------- #
    def load_summaries(self):
        if os.path.exists(self.summaries_file):
            try:
                with open(self.summaries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [PeriodicSummary.from_dict(summary) for summary in data]
            except json.JSONDecodeError as e:
                print(f"加载阶段性总结时出错: {e}")
                return []
            except Exception as e:
                print(f"加载阶段性总结时出错: {e}")
                return []
        return []

    def save_summaries(self, summaries):
        try:
            data = [summary.to_dict() for summary in summaries]
            with open(self.summaries_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存阶段性总结时出错: {e}")

    # ----------------- 项目数据管理 ----------------- #
    def load_projects(self):
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    projects = [Project.from_dict(project) for project in data]
                    # 关联能力标签
                    ability_dict = {ability.name: ability for ability in self.load_abilities()}
                    for project in projects:
                        project.abilities = [ability_dict.get(a.name, AbilityTag(a.name)) for a in project.abilities]
                    return projects
            except json.JSONDecodeError as e:
                print(f"加载项目时出错: {e}")
                return []
            except Exception as e:
                print(f"加载项目时出错: {e}")
                return []
        return []

    def save_projects(self, projects):
        try:
            # 调试信息：检查每个项目的能力标签是否为 AbilityTag 对象
            for project in projects:
                for ability in project.abilities:
                    if not isinstance(ability, AbilityTag):
                        print(f"项目 '{project.name}' 的能力标签 '{ability}' 不是 AbilityTag 对象")
                        raise TypeError(f"能力标签必须是 AbilityTag 对象，但得到的是 '{type(ability)}'")

            data = [project.to_dict() for project in projects]

            # 使用临时文件保存数据
            with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as tf:
                json.dump(data, tf, ensure_ascii=False, indent=4)
                temp_name = tf.name

            # 替换原文件
            shutil.move(temp_name, self.projects_file)
        except TypeError as e:
            print(f"保存项目时出错: {e}")
        except Exception as e:
            print(f"保存项目时出错: {e}")

    # ----------------- 能力标签数据管理 ----------------- #
    def load_abilities(self):
        if os.path.exists(self.abilities_file):
            try:
                with open(self.abilities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [AbilityTag.from_dict(ability) for ability in data]
            except json.JSONDecodeError as e:
                print(f"加载能力标签时出错: {e}")
                return [AbilityTag("无")]
            except Exception as e:
                print(f"加载能力标签时出错: {e}")
                return [AbilityTag("无")]
        return [AbilityTag("无")]

    def save_abilities(self, abilities):
        try:
            data = [ability.to_dict() for ability in abilities]
            with open(self.abilities_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存能力标签时出错: {e}")

    # ----------------- 自动同步每日进度 ----------------- #
    def synchronize_daily_progress(self):
        """
        根据任务的进度历史自动同步每日进度。
        """
        tasks = self.load_tasks()
        daily_progress_list = self.load_daily_progress()

        # 使用 defaultdict 聚合每一天的任务完成数
        progress_counter = defaultdict(int)

        for task in tasks:
            for entry in task.progress_history:
                timestamp, description, progress = entry
                date_str = timestamp.split(' ')[0]  # 提取日期部分
                progress_counter[date_str] += 1  # 假设每次进度更新计为一个完成任务

        # 将聚合结果与现有的每日进度列表对比，并更新或添加条目
        existing_dates = {dp.progress_date for dp in daily_progress_list}

        for date_str, count in progress_counter.items():
            if date_str in existing_dates:
                # 更新已存在的条目
                dp = next(dp for dp in daily_progress_list if dp.progress_date == date_str)
                dp.tasks_completed += count  # 叠加已完成任务数
            else:
                # 添加新的条目
                new_dp = DailyProgress(progress_date=date_str, tasks_completed=count)
                daily_progress_list.append(new_dp)

        # 保存更新后的每日进度列表
        self.save_daily_progress(daily_progress_list)

    # ----------------- 综合数据管理 ----------------- #
    def load_all_data(self):
        """
        加载所有类型的数据。
        """
        tasks = self.load_tasks()
        diary_entries = self.load_diary_entries()
        summaries = self.load_summaries()
        projects = self.load_projects()
        abilities = self.load_abilities()
        daily_progress = self.load_daily_progress()  # 加载每日进度
        goals = self.load_goals()  # 加载目标

        # 同步每日进度
        self.synchronize_daily_progress()
        daily_progress = self.load_daily_progress()  # 重新加载以获取最新的同步结果

        return {
            'tasks': tasks,
            'diary_entries': diary_entries,
            'summaries': summaries,
            'projects': projects,
            'abilities': abilities,
            'daily_progress': daily_progress,  # 包含每日进度
            'goals': goals  # 包含目标
        }

    def save_all_data(self, tasks, diary_entries, summaries, projects, abilities, daily_progress, goals):
        """
        保存所有类型的数据。
        """
        self.save_tasks(tasks)
        self.save_diary_entries(diary_entries)
        self.save_summaries(summaries)
        self.save_projects(projects)
        self.save_abilities(abilities)
        self.save_daily_progress(daily_progress)  # 保存每日进度
        self.save_goals(goals)  # 保存目标
