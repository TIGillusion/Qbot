import os
import json

class KeyMemory:
    def __init__(self, memory_name, max_keywords=100):
        self.auto_memory_path = "./memory/" + memory_name + "/auto_memory.json"
        self.user_memory_path = "./memory/" + memory_name + "/user_memory.json"
        self.max_keywords = max_keywords

    def load_auto_memory(self):
        if os.path.exists(self.auto_memory_path):
            with open(self.auto_memory_path, "r") as f:
                self.auto_memory = json.load(f)
        else:
            os.makedirs(os.path.dirname(self.auto_memory_path), exist_ok=True)
            with open(self.auto_memory_path, "w") as f:
                json.dump({}, f)
    
    def load_user_memory(self):
        if os.path.exists(self.user_memory_path):
            with open(self.user_memory_path, "r") as f:
                self.user_memory = json.load(f)
        else:
            os.makedirs(os.path.dirname(self.user_memory_path), exist_ok=True)
            with open(self.user_memory_path, "w") as f:
                json.dump({}, f)

    def save_auto_memory(self):
        with open(self.auto_memory_path, "w") as f:
            json.dump(self.auto_memory, f)

    
    def add_auto_memory(self, key, value):
        self.load_auto_memory()
        # auto_memory结构: {key: {"value": value, "count": count}}
        if key in self.auto_memory:
            self.auto_memory[key]["value"] = value
            # 不重置count
        else:
            self.auto_memory[key] = {"value": value, "count": 100.0}  # 初始count为100
        # 超过最大数量，删count最小的key
        if len(self.auto_memory) > self.max_keywords:
            min_count = min(item["count"] for item in self.auto_memory.values())
            min_keys = [k for k, v in self.auto_memory.items() if v["count"] == min_count]
            del self.auto_memory[min_keys[0]]
        self.save_auto_memory()

    def get_auto_memory_from_str(self, str):
        self.load_auto_memory()
        result = ""
        hit_keys = set()
        for key, info in self.auto_memory.items():
            if key in str:
                result += f"{key}: {info['value']}\n"
                info["count"] += 1  # 命中时增加count
                hit_keys.add(key)
        # 未命中的关键词count递减0.01
        for key, info in self.auto_memory.items():
            if key not in hit_keys and info["count"] > 0:
                info["count"] = max(0, round(info["count"] - 0.01, 2))
        self.save_auto_memory()
        return f"\n以下是命中关键词相关参考信息:\n{result}\n"
    
    def get_user_memory_from_str(self, str):
        self.load_user_memory()
        result = ""
        for key, value in self.user_memory.items():
            if key in str:
                result += f"{key}: {value}\n"
        return f"\n以下是命中关键词相关准确信息:\n{result}\n"
