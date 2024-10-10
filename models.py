# models.py

class AbilityTag:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent  # 父能力标签名称，默认为 None

    def to_dict(self):
        return {
            'name': self.name,
            'parent': self.parent
        }

    @staticmethod
    def from_dict(data):
        return AbilityTag(name=data['name'], parent=data.get('parent'))


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
            'abilities': [ability.to_dict() for ability in self.abilities],
            'progress': self.progress,
            'progress_history': self.progress_history
        }

    @staticmethod
    def from_dict(data):
        abilities = []

        # 新格式，abilities 是列表
        if 'abilities' in data:
            abilities_data = data['abilities']
            if isinstance(abilities_data, list):
                abilities = [AbilityTag.from_dict(ability_data) for ability_data in abilities_data]
            elif isinstance(abilities_data, dict):
                abilities.append(AbilityTag.from_dict(abilities_data))
            else:
                abilities = []
        # 旧格式，ability 是单个对象
        elif 'ability' in data:
            ability_data = data['ability']
            if ability_data:
                abilities.append(AbilityTag.from_dict(ability_data))
        else:
            abilities = []

        task = Task(
            name=data['name'],
            due_date=data['due_date'],
            interest=data.get('interest', None),
            description=data.get('description', ''),
            abilities=abilities,
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
