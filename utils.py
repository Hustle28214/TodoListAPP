# utils.py
from tkinter import messagebox

def display_error(title, message):
    """
    显示错误消息框。

    :param title: 消息框标题
    :param message: 消息内容
    """
    messagebox.showerror(title, message)

def display_info(title, message):
    """
    显示信息消息框。

    :param title: 消息框标题
    :param message: 消息内容
    """
    messagebox.showinfo(title, message)

def display_warning(title, message):
    """
    显示警告消息框。

    :param title: 消息框标题
    :param message: 消息内容
    """
    messagebox.showwarning(title, message)
