import os
import json
import math
import heapq
import time
from datetime import datetime
from module.funcs import stream_request_AI, generate_response


class MEM_I():

    def __init__(self,
                 AI_name,
                 model_config,
                 memory_path = "./memory/mem_i",
                 memory_file = "memory.json"):
        self.AI_name = AI_name
        self.model_config = model_config
        if not os.path.exists(memory_path):
            os.makedirs(memory_path)
        self.memory_path = memory_path + "/" + memory_file
        if not os.path.exists(self.memory_path):
            self.memory_json = {}
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_json, f, ensure_ascii=False, indent=4)
        self.refresh_memory_json()

    def refresh_memory_json(self):
        with open(self.memory_path, 'r', encoding='utf-8') as f:
            self.memory_json = json.load(f)
        return self.memory_json
    
    def _convey_history_2_context(self, history):
        context = ""
        for per_role in history:
            if per_role["role"] == "user":
                context += f"|<user>|:{per_role['content']}\n\n"
            elif per_role["role"] == "assistant":
                context += f"|<assistant>|:{per_role['content']}\n\n"
        return context

    def add_memory(self, history):
        context = self._convey_history_2_context(history)
        summary = self._get_summary(context)[:300]
        self.memory_json[summary] = {
            "content": context,
            "timestamp": time.time()
        }
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory_json, f, ensure_ascii=False, indent=4)
        
    def _get_summary(self, context):
        system_prompt = """
你的任务是将复杂混乱的聊天内容进行总结，要求：主次分明，概括事件，忽略聊天记录中的代码部分（这是无效内容）"""
        message = f"{context.replace('|<assistant>|',self.AI_name)}\n以上内容是一段复杂的聊天记录，请你将其概括总结，注重强调其中提到的新鲜内容如：梗，知识点，关键信息等。总结字数为200字以内。"
        history = []
        response=stream_request_AI(system_prompt, message, history, self.model_config)
        response_raw_str=generate_response(response)
        return response_raw_str

    def search_texts(self, texts, keywords, top_k=10):
        """Return up to top_k texts ranked by keyword relevance."""
        if not texts or not keywords:
            return []

        normalized = [kw.strip().lower() for kw in keywords if kw and kw.strip()]
        if not normalized:
            return []

        total_texts = len(texts)
        keyword_df = {kw: 0 for kw in normalized}
        lowered_texts = []

        for text in texts:
            if not isinstance(text, str):
                text = str(text)
            text_lower = text.lower()
            lowered_texts.append(text_lower)
            for kw in keyword_df:
                if kw in text_lower:
                    keyword_df[kw] += 1

        keyword_weights = {
            kw: 1.0 + math.log((total_texts + 1) / (df + 1))
            for kw, df in keyword_df.items()
        }

        scored = []
        for idx, (text, text_lower) in enumerate(zip(texts, lowered_texts)):
            score = self._score_text(text_lower, normalized, keyword_weights)
            if score > 0:
                scored.append((score, -idx, text))

        if not scored:
            return []

        top_items = heapq.nlargest(top_k, scored)
        return [text for _, _, text in top_items]

    def _score_text(self, text_lower, keywords, keyword_weights):
        score = 0.0
        hits = 0

        for kw in keywords:
            if kw in text_lower:
                count = text_lower.count(kw)
                weight = keyword_weights.get(kw, 1.0)
                score += count * (weight + min(len(kw), 8) * 0.1)
                hits += 1

        if score > 0 and hits == len(keywords):
            score += sum(keyword_weights.get(kw, 1.0) for kw in keywords)

        return score

    def search_dict_items(self, data_dict, keywords, top_k=10):
        """Return up to top_k dicts with key/value/score ranked by relevance."""
        if not data_dict or not keywords:
            return []

        normalized = [kw.strip().lower() for kw in keywords if kw and kw.strip()]
        if not normalized:
            return []

        items = list(data_dict.items())
        total_items = len(items)
        keyword_df = {kw: 0 for kw in normalized}
        combined_texts = []

        for key, value in items:
            key_text = str(key)
            value_text = self._extract_memory_content(value)
            combined = (key_text + " " + value_text).lower()
            combined_texts.append((key_text.lower(), value_text.lower()))
            for kw in keyword_df:
                if kw in combined:
                    keyword_df[kw] += 1

        keyword_weights = {
            kw: 1.0 + math.log((total_items + 1) / (df + 1))
            for kw, df in keyword_df.items()
        }

        scored = []
        for idx, ((key, value), (key_lower, value_lower)) in enumerate(zip(items, combined_texts)):
            key_score = self._score_text(key_lower, normalized, keyword_weights)
            value_score = self._score_text(value_lower, normalized, keyword_weights)
            total_score = key_score * 10.0 + value_score
            if total_score > 0:
                scored.append((total_score, -idx, (key, value)))

        if not scored:
            return []

        top_items = heapq.nlargest(top_k, scored)
        return [
            {"key": key, "value": value, "score": score}
            for score, _, (key, value) in top_items
        ]
    
    def search_querys(self, querys, top_k, max_tokens):
        relative = self.search_dict_items(self.memory_json, querys, top_k)
        result = ""
        key_result = ""
        for n in range(0, len(relative)):
            display_value = self._render_memory_with_time(relative[n]["value"])
            result += f"{n+1}.{display_value}\n"
        if not result:
            result = "未查询到与关键词相关信息"
        for n in range(0, len(relative)):
            key_result += f"{n+1}.{relative[n]['key']}\n"
        if not result:
            key_result = "未查询到与关键词相关信息"
        if len(result) > max_tokens * 3:
            auto_result = key_result[:max_tokens]
        else:
            auto_result = result[:max_tokens]
        return auto_result, result[:max_tokens], key_result[:max_tokens]

    def _extract_memory_content(self, value):
        if isinstance(value, dict):
            return str(value.get("content", ""))
        return str(value)

    def _render_memory_with_time(self, value):
        if isinstance(value, dict):
            content = str(value.get("content", ""))
            timestamp = value.get("timestamp")
            time_desc = self._format_time_delta(timestamp)
            if time_desc:
                return f"{time_desc} {content}"
            return content
        return str(value)

    def _format_time_delta(self, timestamp):
        if not timestamp:
            return ""
        try:
            ts = float(timestamp)
        except (TypeError, ValueError):
            return ""

        now = datetime.now()
        dt = datetime.fromtimestamp(ts)
        diff_seconds = max(0, int((now - dt).total_seconds()))
        diff_days = (now.date() - dt.date()).days

        if diff_seconds < 60:
            return "刚刚"
        if diff_seconds < 3600:
            minutes = max(1, diff_seconds // 60)
            return f"{minutes}分钟前"
        if diff_seconds < 3 * 3600:
            hours = max(1, diff_seconds // 3600)
            return f"{hours}小时前"

        if diff_days == 0:
            return f"今日{self._format_period_time(dt)}"
        if diff_days == 1:
            return f"昨天{self._format_period_time(dt)}"
        if diff_days == 2:
            return f"前天{self._format_period_time(dt)}"
        if diff_days == 3:
            return "三天前"
        if 4 <= diff_days <= 7:
            return f"{diff_days}天前"

        return self._format_full_datetime(dt)

    def _format_period_time(self, dt):
        hour = dt.hour
        minute = dt.minute

        if 0 <= hour <= 5:
            period = "凌晨"
        elif 6 <= hour <= 11:
            period = "上午"
        elif 12 <= hour <= 13:
            period = "中午"
        elif 14 <= hour <= 17:
            period = "下午"
        else:
            period = "晚上"

        display_hour = hour
        if period in ("下午", "晚上"):
            display_hour = hour - 12 if hour > 12 else hour

        time_part = f"{display_hour}点"
        if minute:
            time_part += f"{minute}分"
        return f"{period}{time_part}"

    def _format_full_datetime(self, dt):
        period_time = self._format_period_time(dt)
        second = dt.second
        if second:
            period_time += f"{second}秒"
        return f"{dt.year}年{dt.month}月{dt.day}日{period_time}"
    
    def agent_search(self, querys, history):
        t_history = []
        for n in range(0, 10):
            querys = querys.split(" ")
            search_result, _, _ = self.search_querys(querys, top_k=5, max_tokens=20000)
            context = self._convey_history_2_context(history)
            system_prompt = """
    你是一个有用的Agent助理，负责从文本中分析信息
    要求：
    1.使用如下的严格的json格式回复：
    ```json
    {
        "reason":"这里是分析的过程", # 每次必须包含分析的过程
        "querys":"keyword1 keyword2 ...", # 如果关键词未找到足够信息，接下来需要搜索新的关键词，关键词间用空格隔开，如果信息已足够回答问题，则不再填写此项，必须留空
        "answer":"分析足够信息后的答复" # 最终答复，如果信息不够不足以给出答复则此项必须留空，如果信息足够给出答复则详细答复并不需要写关键词
        }
    ```
    2.仔细分析，做到有理有据，回复除了正常的分析之外，每次必须包含一个json格式段，最终回答详细一些
    """     
            if n == 0:
                message = f"""
    {context.replace("|<assistant>|",self.AI_name)}\n以上内容是一段复杂的聊天记录，根据语境这时候需要你查询{str(querys)}相关信息，你也可以检索结果进一步的一步步检索其他更多关键词，弄明白其含义和关联，并最终整理为一个报告，汇报相关情况以应对当前语境需要，现在已根据关键词“{str(querys)}”查到了以下相关内容：\n{search_result}\n结合上下文分析，如果信息足够就按照以下格式回复：""" 
            else:
                message = f"""
现在已根据新的关键词“{str(querys)}”查到了以下相关内容，你可以选择进一步检索新的关键词或开始汇报：\n{search_result}\n结合上下文分析，如果信息足够就按照以下格式回复："""    
                message += """
    ```json
    {
        "reason":"这里是分析的过程",
        "querys":"", # 如果目前信息足以给出最终答复，则此项必须留空
        "answer":"这里是最终答复"
        }
    ```
    如果之前检索的关键词未找到相关信息或找到的信息不足，需要进一步更换并检索新的其他关键词，则使用如下格式回复：
    ···json
    {
        "reason":"这里是分析的过程",
        "querys":"keyword1 keyword2 ...", # 关键词中间使用空格分隔
        "answer":"" # 如果目前信息不足以给出最终答复，则此项必须留空
        }
    ```
    当检索次数超过五轮后即停止检索并尽可能根据已检索到的信息完成汇报内容
    """
            response=stream_request_AI(system_prompt, message, message_history = t_history, model_config = self.model_config)
            response_raw_str=generate_response(response)
            json_str = response_raw_str.replace("```json","").replace("```","")
            try:
                json_dict = json.loads(json_str)
                querys = json_dict.get("querys","")
                answer = json_dict.get("answer","")
                reason = json_dict.get("reason","")
                if querys and answer and n < 4:
                    t_history.append(
                        {"role":"user",
                         "content":message}
                    )
                    t_history.append(
                        {"role":"assistant",
                         "content":response_raw_str}
                    )
                    continue
                elif answer:
                    return f"来自智能检索系统分析：{reason}\n回答：{answer}"
                elif querys:
                    t_history.append(
                        {"role":"user",
                         "content":message}
                    )
                    t_history.append(
                        {"role":"assistant",
                         "content":response_raw_str}
                    )
                else:
                    message += "\n注意严格按照格式回复"
            except Exception as e:
                print("mem_i: error:" + e)
                message += "\n注意严格按照格式回复"



if __name__ == "__main__":
    mem = MEM_I("幻蓝",
                {
            "model_api": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "model_name": "GLM-4-Flash",
            "model_key": "31598f74ee9776d64b85b0a0457d9094.EKpxafHYqcpiElrE",
            "weight": 0
        })
    result = mem.agent_search("喜欢 食物",[{
        "role":"user",
        "content":"幻蓝你喜欢吃什么？"
    }])
    print(result)
    # sample_texts = [
    #     "Qbot starts with start.bat and uses bundled python.",
    #     "Memory system stores long_memory and mid_memory.",
    #     "Trigger keywords mention the fox spirit and year.",
    #     "This line does not match.",
    # ]
    # print(mem.search_texts(sample_texts, ["memory", "python", "fox"], top_k=3))

    # sample_dict = {
    #     "memory_path": "memory/long_memory.txt for long context",
    #     "start_cmd": "start.bat runs Qbot_all.py",
    #     "fox_alias": "fox spirit nickname appears in prompts",
    #     "random": "unrelated text",
    # }
    # print(mem.search_dict_items(sample_dict, ["memory", "fox", "start"], top_k=3))
