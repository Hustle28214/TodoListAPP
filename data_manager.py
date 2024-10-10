# data_manager.py
import json
import os
from models import Task, DiaryEntry, PeriodicSummary, Project, AbilityTag
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


    # ----------------- 日记数据管理 ----------------- #
    def load_diary_entries(self):
        if os.path.exists(self.diary_file):
            try:
                with open(self.diary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
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
                    return [Project.from_dict(project) for project in data]
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
        return {
            'tasks': tasks,
            'diary_entries': diary_entries,
            'summaries': summaries,
            'projects': projects,
            'abilities': abilities
        }

    def save_all_data(self, tasks, diary_entries, summaries, projects, abilities):
        """
        保存所有类型的数据。
        """
        self.save_tasks(tasks)
        self.save_diary_entries(diary_entries)
        self.save_summaries(summaries)
        self.save_projects(projects)
        self.save_abilities(abilities)
