import tkinter as tk
import queue
from tkinter import *
from tkinter import ttk
from script import getUrl, fetchConfig, startProgram
import threading
import os
import time
import base64
from icon.icon import Icon
import tempfile


class Script(threading.Thread):
    def __init__(self, command_queue, msg_queue):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.command_queue = command_queue
        self.ss_process = None

    def run(self):
        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                if command == -1:
                    return self.kill_ss()  # 使用return使子进程退出
                elif command == 0:
                    self.fetch_ip_and_start()
                elif command == 1:
                    self.fetch_ip()
                elif command == 2:
                    self.kill_ss()
                    while self.ss_process is not None:
                        pass
                    self.fetch_ip_and_start()
            else:
                time.sleep(0.1)

    def fetch_ip_and_start(self):
        self.msg_queue.put("获取URL...")
        self.msg_queue.put("URL解析成功：" + getUrl())
        self.msg_queue.put("获取IP...")
        res = fetchConfig()
        if res:
            self.msg_queue.put("获取IP成功，启动SS...")
            self.ss_process = startProgram()
            self.msg_queue.put("启动SS完成")

        else:
            self.msg_queue.put("获取IP失败")

    def fetch_ip(self):
        self.msg_queue.put("获取IP...")
        res = fetchConfig()
        if res:
            self.msg_queue.put("获取IP成功")
        else:
            self.msg_queue.put("获取IP失败")

    def kill_ss(self):
        self.msg_queue.put("结束SS进程...")
        if self.ss_process is not None and self.ss_process.kill() is None:
            self.ss_process = None
        self.msg_queue.put("SS进程结束")


class AutoSS(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.msg_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.process_msg()
        self.script = Script(self.command_queue, self.msg_queue)
        self.script.start()
        self.command_queue.put(0)  # 启动程序则开始抓取

    def createWidgets(self):
        fm1 = Frame(self)
        fm1.pack(fill=X, expand=YES, side=TOP, padx=6, pady=4)
        self.display_info = tk.Listbox(fm1, width=50)
        self.display_info.pack(side=LEFT, fill=X, expand=YES)
        vertical_bar = ttk.Scrollbar(fm1, orient=VERTICAL, command=self.display_info.yview)
        vertical_bar.pack(side=RIGHT, fill=Y)
        self.display_info['yscrollcommand'] = vertical_bar.set

        fm2 = Frame(self.master)
        fm2.pack(side=BOTTOM, padx=10, pady=3, expand=YES)
        ttk.Button(fm2, text='退出', command=self.safe_destroy).pack(side=LEFT, fill=Y, expand=YES, padx=10)
        ttk.Button(fm2, text='更新IP', command=self.update_ip).pack(side=LEFT, fill=Y, expand=YES, padx=10)
        ttk.Button(fm2, text='重新启动', command=self.restart).pack(side=LEFT, fill=Y, expand=YES, padx=10)

    def start_up(self):
        self.command_queue.put(0)

    def update_ip(self):
        self.command_queue.put(1)

    def restart(self):
        self.command_queue.put(2)

    def safe_destroy(self):
        self.display_info.insert(0, "退出SS...")
        self.command_queue.put(-1)
        cnt = 0
        while True:
            if self.script.ss_process is None:
                # SS退出完成
                root.destroy()
                break
            else:
                cnt += 1
                time.sleep(1)
            if cnt >= 5:
                self.display_info.insert(0, "SS退出失败，请重试")
                break

    def process_msg(self):
        self.after(400, self.process_msg)
        while not self.msg_queue.empty():
            try:
                msg = self.msg_queue.get()
                self.display_info.insert(0, msg, )
            except queue.Empty:
                pass


if __name__ == '__main__':
    root = tk.Tk()
    root.title("AutoSS")
    root.geometry("400x250")
    temp_icon = os.path.join(tempfile.gettempdir(), 'tmp.ico')
    with open(temp_icon, 'wb+') as tmp:
        tmp.write(base64.b64decode(Icon.img))
    root.resizable(False, False)
    root.standard_font = (None, 16)
    root.iconbitmap(temp_icon)  # 放在所有设置之后，否则启动时会闪烁一次
    app = AutoSS(master=root)
    root.mainloop()
