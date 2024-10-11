# models.py

class KnowledgePoint:
    def __init__(self, content, learned=False):
        self.content = content
        self.learned = learned

    def to_dict(self):
        return {
            'content': self.content,
            'learned': self.learned
        }

    @staticmethod
    def from_dict(data):
        return KnowledgePoint(
            content=data['content'],
            learned=data.get('learned', False)
        )


class AbilityTag:
    def __init__(self, name, parent=None, knowledge_points=None):
        self.name = name
        self.parent = parent  # 父能力标签名称，默认为 None
        self.knowledge_points = knowledge_points if knowledge_points else []  # List of KnowledgePoint

    def to_dict(self):
        return {
            'name': self.name,
            'parent': self.parent,
            'knowledge_points': [kp.to_dict() for kp in self.knowledge_points]
        }

    @staticmethod
    def from_dict(data):
        knowledge_points_data = data.get('knowledge_points', [])
        knowledge_points = [KnowledgePoint.from_dict(kp) for kp in knowledge_points_data]
        return AbilityTag(name=data['name'], parent=data.get('parent'), knowledge_points=knowledge_points)


class Task:
    def __init__(self, name, due_date, interest=None, description='', abilities=None, progress=0):
        self.name = name
        self.due_date = due_date  # 字符串格式：YYYY-MM-DD
        self.interest = interest  # 整数，1-5，默认为 None
        self.description = description
        self.abilities = abilities if abilities else []  # List of AbilityTag objects
        self.progress = progress  # 整数，0-100
        self.progress_history = []  # List of tuples: (timestamp, description, progress)

    def to_dict(self):
        return {
            'name': self.name,
            'due_date': self.due_date,
            'interest': self.interest,
            'description': self.description,
            'abilities': [ability.to_dict() for ability in self.abilities],  # 确保这是一个列表
            'progress': self.progress,
            'progress_history': self.progress_history
        }

    @staticmethod
    def from_dict(data):
        abilities_data = data.get('abilities', [])
        abilities = []

        # 处理旧格式，abilities_data 是单个对象的情况
        if isinstance(abilities_data, dict):
            abilities.append(AbilityTag.from_dict(abilities_data))
        # 处理新格式，abilities_data 是列表的情况
        elif isinstance(abilities_data, list):
            abilities = [AbilityTag.from_dict(ability_data) for ability_data in abilities_data]
        # abilities_data 为空或为 None 的情况
        else:
            abilities = []

        task = Task(
            name=data['name'],
            due_date=data['due_date'],
            interest=data.get('interest', None),
            description=data.get('description', ''),
            abilities=abilities,  # 这里确保 abilities 是一个列表
            progress=data.get('progress', 0)
        )
        task.progress_history = data.get('progress_history', [])
        return task

# models.py
from datetime import datetime, date

class DiaryEntry:
    def __init__(self, entry_date, summary, category='', tags=None, links=None):
        if isinstance(entry_date, str):
            try:
                self.entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError as e:
                print(f"错误：无法解析日期 '{entry_date}'，错误信息：{e}")
                self.entry_date = None
        elif isinstance(entry_date, date):
            self.entry_date = entry_date
        else:
            raise TypeError("entry_date must be a string or datetime.date instance")
        self.summary = summary
        self.category = category
        self.tags = tags if tags else []
        self.links = links if links else []

    def to_dict(self):
        return {
            'entry_date': self.entry_date.strftime('%Y-%m-%d') if self.entry_date else '',
            'summary': self.summary,
            'category': self.category,
            'tags': [tag.to_dict() for tag in self.tags],
            'links': self.links
        }

    @staticmethod
    def from_dict(data):
        tags = [AbilityTag.from_dict(tag) for tag in data.get('tags', [])]
        entry_date_str = data.get('entry_date', '')
        if entry_date_str:
            try:
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            except ValueError as e:
                print(f"错误：无法解析日期 '{entry_date_str}'，错误信息：{e}")
                entry_date = None
        else:
            entry_date = None
        return DiaryEntry(
            entry_date=entry_date,
            summary=data.get('summary', ''),
            category=data.get('category', ''),
            tags=tags,
            links=data.get('links', [])
        )



class PeriodicSummary:
    def __init__(self, title, content, summary_date):
        self.title = title
        self.content = content
        self.summary_date = summary_date  # 字符串格式：YYYY-MM-DD

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'summary_date': self.summary_date
        }

    @staticmethod
    def from_dict(data):
        return PeriodicSummary(
            title=data['title'],
            content=data['content'],
            summary_date=data['summary_date']
        )


class Project:
    def __init__(self, name, due_date, abilities, description, progress=0, interest=None, progress_history=None):
        self.name = name
        self.due_date = due_date  # 字符串格式：YYYY-MM-DD
        self.abilities = abilities  # List of AbilityTag objects
        self.description = description
        self.progress = progress  # 整数，0-100
        self.interest = interest  # 可选的整数，1-5
        self.progress_history = progress_history if progress_history is not None else []  # List of tuples: (timestamp, description, progress)

    def to_dict(self):
        data = {
            'name': self.name,
            'due_date': self.due_date,
            'abilities': [ability.to_dict() for ability in self.abilities],
            'description': self.description,
            'progress': self.progress,
            'progress_history': self.progress_history
        }
        if self.interest is not None:
            data['interest'] = self.interest
        return data

    @staticmethod
    def from_dict(data):
        abilities = [AbilityTag.from_dict(a) for a in data.get('abilities', [])]
        interest = data.get('interest')  # 可能为 None
        progress_history = data.get('progress_history', [])  # 可能为空列表
        return Project(
            name=data['name'],
            due_date=data['due_date'],
            abilities=abilities,
            description=data['description'],
            progress=data.get('progress', 0),
            interest=interest,
            progress_history=progress_history
        )
class DailyProgress:
    def __init__(self, progress_date, tasks_completed=0, notes='', tags=None):
        """
        :param progress_date: 日期，字符串格式 YYYY-MM-DD
        :param tasks_completed: 完成的任务数，整数
        :param notes: 备注，字符串
        :param tags: 标签，列表，包含 AbilityTag 对象
        """
        self.progress_date = progress_date
        self.tasks_completed = tasks_completed
        self.notes = notes
        self.tags = tags if tags else []

    def to_dict(self):
        return {
            'progress_date': self.progress_date,
            'tasks_completed': self.tasks_completed,
            'notes': self.notes,
            'tags': [tag.to_dict() for tag in self.tags]
        }

    @staticmethod
    def from_dict(data):
        tags_data = data.get('tags', [])
        tags = [AbilityTag.from_dict(tag_data) for tag_data in tags_data]
        return DailyProgress(
            progress_date=data['progress_date'],
            tasks_completed=data.get('tasks_completed', 0),
            notes=data.get('notes', ''),
            tags=tags
        )

        # models.py

class Goal:
    def __init__(self, text, due_date, completed=False):
        self.text = text
        self.due_date = due_date
        self.completed = completed

    def to_dict(self):
        return {
            "text": self.text,
            "due_date": self.due_date,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            text=data.get("text", ""),
            due_date=data.get("due_date", ""),
            completed=data.get("completed", False)
        )
