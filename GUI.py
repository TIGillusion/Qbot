import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json


class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("幻宙娘AI配置编辑器")
        self.config_data = {}
        self.master.minsize(400, 600)  # 设置最小窗口尺寸

        # 创建滚动条容器
        self.canvas = tk.Canvas(master)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置画布滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局组件
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.create_widgets()
        self.load_config()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):
        # 公共设置
        self.create_common_settings()
        # API设置
        self.create_api_settings()
        # 角色设置
        self.create_character_settings()
        # 主动设置
        self.create_active_settings()
        # 戳一戳设置
        self.create_poke_settings()
        # 绘图设置
        self.create_draw_settings()
        # 按钮区
        self.create_buttons()

    def create_common_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="基础设置")
        frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # 设置列权重
        frame.columnconfigure(1, weight=1)

        # Socket端口号
        ttk.Label(frame, text="Socket端口号：").grid(row=0, column=0, sticky="e", padx=5)
        self.socket_number = ttk.Entry(frame, width=10)
        self.socket_number.grid(row=0, column=1, sticky="ew", padx=5)

        # 最大字数
        ttk.Label(frame, text="最大字数：").grid(row=1, column=0, sticky="e", padx=5)
        self.max_ac_word = ttk.Entry(frame, width=8)
        self.max_ac_word.grid(row=1, column=1, sticky="ew", padx=5)

        # QQ名称
        ttk.Label(frame, text="QQ名称：").grid(row=2, column=0, sticky="e", padx=5)
        self.qq_name = ttk.Entry(frame, width=20)
        self.qq_name.grid(row=2, column=1, sticky="ew", padx=5)

        # 触发词
        ttk.Label(frame, text="触发词：").grid(row=3, column=0, sticky="e", padx=5)
        self.trigger = ttk.Entry(frame)
        self.trigger.grid(row=3, column=1, sticky="ew", padx=5)

        # 管理员ID
        ttk.Label(frame, text="管理员ID：").grid(row=4, column=0, sticky="e", padx=5)
        self.root_id = ttk.Entry(frame)
        self.root_id.grid(row=4, column=1, sticky="ew", padx=5)

    def create_api_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="API设置")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        frame.columnconfigure(1, weight=1)

        # 聊天API
        ttk.Label(frame, text="聊天URL：").grid(row=0, column=0, sticky="e")
        self.chat_url = ttk.Entry(frame,)
        self.chat_url.grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="API密钥：").grid(row=1, column=0, sticky="e")
        self.chat_key = ttk.Entry(frame)
        self.chat_key.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="模型名称：").grid(row=2, column=0, sticky="e")
        self.chat_model = ttk.Entry(frame)
        self.chat_model.grid(row=2, column=1, sticky="ew")

        # 绘图API
        ttk.Label(frame, text="绘图URL：").grid(row=3, column=0, sticky="e")
        self.draw_url = ttk.Entry(frame)
        self.draw_url.grid(row=3, column=1, sticky="ew")

        ttk.Label(frame, text="绘图密钥：").grid(row=4, column=0, sticky="e")
        self.draw_key = ttk.Entry(frame)
        self.draw_key.grid(row=4, column=1, sticky="ew")

        ttk.Label(frame, text="绘图模型：").grid(row=5, column=0, sticky="e")
        self.draw_model = ttk.Entry(frame)
        self.draw_model.grid(row=5, column=1, sticky="ew")

    def create_character_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="角色设定")
        frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # 系统提示1
        ttk.Label(frame, text="系统提示1：").grid(row=0, column=0, sticky="ne")
        self.system_prompt = scrolledtext.ScrolledText(frame, width=60, height=8)
        self.system_prompt.grid(row=0, column=1, sticky="ew")

        # 系统提示2
        ttk.Label(frame, text="系统提示2：").grid(row=1, column=0, sticky="ne")
        self.system_prompt2 = scrolledtext.ScrolledText(frame, width=60, height=8)
        self.system_prompt2.grid(row=1, column=1, sticky="ew")

    def create_active_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="主动设置")
        frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.active = tk.BooleanVar()
        ttk.Checkbutton(frame, text="启用主动聊天", variable=self.active).grid(row=0, column=0)

        ttk.Label(frame, text="群主动发消息：").grid(row=1, column=0, sticky="e")
        self.active_group = ttk.Entry(frame)
        self.active_group.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="私聊主动发消息：").grid(row=2, column=0, sticky="e")
        self.active_private = ttk.Entry(frame)
        self.active_private.grid(row=2, column=1, sticky="ew")

    def create_poke_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="戳一戳设置")
        frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.poke = tk.BooleanVar()
        ttk.Checkbutton(frame, text="启用戳一戳", variable=self.poke).grid(row=0, column=0)

        ttk.Label(frame, text="BV号列表：").grid(row=1, column=0, sticky="e")
        self.BV_number = ttk.Entry(frame)
        self.BV_number.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="戳一戳消息：").grid(row=2, column=0, sticky="e")
        self.poke_message = ttk.Entry(frame)
        self.poke_message.grid(row=2, column=1, sticky="ew")

    def create_draw_settings(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="绘图设置")
        frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        self.draw = tk.BooleanVar()
        ttk.Checkbutton(frame, text="启用本地绘图功能", variable=self.draw).grid(row=0, column=0)

        ttk.Label(frame, text="绝对路径：").grid(row=1, column=0, sticky="e")
        self.absolute_path = ttk.Entry(frame)
        self.absolute_path.grid(row=1, column=1, sticky="ew")
        ttk.Button(frame, text="浏览", command=self.browse_path).grid(row=1, column=2)

    def create_buttons(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=6, column=0, padx=10, pady=10, sticky="e")

        ttk.Button(frame, text="保存配置", command=self.save_config).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="退出程序", command=self.master.destroy).grid(row=0, column=1, padx=5)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.absolute_path.delete(0, tk.END)
            self.absolute_path.insert(0, path)

    def load_config(self):
        try:
            with open("set.json", "r", encoding="utf-8") as f:
                self.config_data = json.load(f)

            # 基础设置
            self.socket_number.insert(0, str(self.config_data["socket_number"]))
            self.max_ac_word.insert(0, str(self.config_data["max_ac_word"]))
            self.qq_name.insert(0, self.config_data["qq_name"])
            self.trigger.insert(0, self.config_data["trigger"])
            self.root_id.insert(0, ", ".join(self.config_data["root_id"]))

            # API设置
            self.chat_url.insert(0, self.config_data["chat_url"])
            self.chat_key.insert(0, self.config_data["chat_key"])
            self.chat_model.insert(0, self.config_data["chat_model"])
            self.draw_url.insert(0, self.config_data["draw_url"])
            self.draw_key.insert(0, self.config_data["draw_key"])
            self.draw_model.insert(0, self.config_data["draw_model"])

            # 角色设置
            self.system_prompt.insert("1.0", self.config_data["system_prompt"])
            self.system_prompt2.insert("1.0", self.config_data["system_prompt2"])

            # 主动设置
            self.active.set(self.config_data["active"] == "true")
            self.active_group.insert(0, self.config_data["active_group"])
            self.active_private.insert(0, self.config_data["active_private"])

            # 戳一戳设置
            self.poke.set(self.config_data["poke"] == "true")
            self.BV_number.insert(0, ", ".join(self.config_data["BV_number"]))
            self.poke_message.insert(0, ", ".join(self.config_data["poke_message"]))

            # 绘图设置
            self.draw.set(self.config_data["draw"] == "true")
            self.absolute_path.insert(0, self.config_data["absolute_path"].strip('r"'))

        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败：{str(e)}")

    def save_config(self):
        try:
            new_config = {
                "socket_number": int(self.socket_number.get()),
                "max_ac_word": int(self.max_ac_word.get()),
                "qq_name": self.qq_name.get(),
                "root_id": [x.strip() for x in self.root_id.get().split(",")],
                "trigger": self.trigger.get(),
                "chat_url": self.chat_url.get(),
                "chat_key": self.chat_key.get(),
                "chat_model": self.chat_model.get(),
                "draw_url": self.draw_url.get(),
                "draw_key": self.draw_key.get(),
                "draw_model": self.draw_model.get(),
                "system_prompt": self.system_prompt.get("1.0", "end-1c"),
                "system_prompt2": self.system_prompt2.get("1.0", "end-1c"),
                "active": "true" if self.active.get() else "false",
                "active_group": self.active_group.get(),
                "active_private": self.active_private.get(),
                "active_goal": "true",
                "set_time": "00",
                "poke": "true" if self.poke.get() else "false",
                "BV_number": [x.strip() for x in self.BV_number.get().split(",")],
                "poke_message": [x.strip() for x in self.poke_message.get().split(",")],
                "draw": "true" if self.draw.get() else "false",
                "absolute_path": f'r"{self.absolute_path.get()}"'
            }

            with open("set.json", "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("成功", "配置保存成功！")

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")  # 设置初始窗口大小
    app = ConfigEditor(root)
    root.mainloop()