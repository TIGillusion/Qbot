import argparse
import json
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


DEFAULT_MODEL = "glm-4.7"
DEFAULT_API_BASE = "http://<IP>:9000/v1/chat/completions"
DEFAULT_API_KEY_LIST = ["key1", "key2", "key3"]  # 替换为实际的API密钥列表
DEFAULT_CONFIG = "soups.json"

ALLOWED_SHORT_ANSWERS = {"是", "否", "无关", "不确定"}
ASK_YES_NO = "请用是/否问题"


@dataclass
class SoupConfig:
    surface: str
    bottom: str
    objective: str
    max_questions: int
    allow_hints: bool
    hints: List[str]
    title: str = ""


@dataclass
class GameState:
    questions_asked: int = 0
    ended: bool = False


def _get_first_value(data: Dict[str, Any], keys: List[str]) -> Optional[Any]:
    for key in keys:
        if key in data:
            return data[key]
    return None


def _load_soups(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("soups"), list):
        return data["soups"]
    if isinstance(data, dict):
        return [data]
    raise ValueError("配置文件格式不正确")


def _select_soup_entry(
    soups: List[Dict[str, Any]],
    soup_id: Optional[str],
    soup_index: Optional[int],
) -> Dict[str, Any]:
    if not soups:
        raise ValueError("未提供任何汤")
    if soup_index is not None:
        idx = soup_index - 1
        if idx < 0 or idx >= len(soups):
            raise ValueError("soup_index 超出范围")
        return soups[idx]
    if soup_id:
        for item in soups:
            candidate = _get_first_value(item, ["id", "name", "标题", "title"])
            if candidate is not None and str(candidate) == soup_id:
                return item
        raise ValueError("未找到匹配的 soup_id")
    return random.choice(soups)


def _build_config(data: Dict[str, Any]) -> SoupConfig:
    surface = _get_first_value(data, ["汤面", "surface", "soup_surface"])
    bottom = _get_first_value(data, ["汤底", "bottom", "soup_bottom"])
    objective = _get_first_value(data, ["任务目标", "objective", "goal"]) or "还原真相"
    max_questions = _get_first_value(data, ["提问次数", "max_questions", "question_limit"])
    allow_hints = bool(_get_first_value(data, ["允许提示", "allow_hints"]))
    hints = _get_first_value(data, ["提示列表", "hints"]) or []
    title = _get_first_value(data, ["标题", "title", "name", "id"]) or ""

    if surface is None or bottom is None:
        raise ValueError("配置缺少汤面或汤底")

    if max_questions is None:
        max_questions = 20

    if not isinstance(hints, list):
        hints = []

    return SoupConfig(
        surface=str(surface),
        bottom=str(bottom),
        objective=str(objective),
        max_questions=int(max_questions),
        allow_hints=allow_hints,
        hints=[str(h) for h in hints],
        title=str(title),
    )


class TurtleSoupHost:
    def __init__(
        self,
        config_path: str = DEFAULT_CONFIG,
        base_url: str = DEFAULT_API_BASE,
        api_key: str = random.choice(DEFAULT_API_KEY_LIST),
        model: str = DEFAULT_MODEL,
        soup_id: Optional[str] = None,
        soup_index: Optional[int] = None,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
        timeout: int = 60,
    ) -> None:
        self.config_path = config_path
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.timeout = timeout
        self.config = self.start_new_game(soup_id, soup_index)
        self.state = GameState()
        self.history: List[Dict[str, str]] = []

    def start_new_game(
        self, soup_id: Optional[str] = None, soup_index: Optional[int] = None
    ) -> SoupConfig:
        soups = _load_soups(self.config_path)
        entry = _select_soup_entry(soups, soup_id, soup_index)
        self.config = _build_config(entry)
        self.state = GameState()
        self.history = []
        return self.config

    def _build_system_prompt(self) -> str:
        remaining = max(self.config.max_questions - self.state.questions_asked, 0)
        hints_text = "、".join(self.config.hints) if self.config.hints else "无"
        return "\n".join(
            [
                "你是海龟汤主持人。",
                "必须严格遵守规则：",
                "1) 绝不直接泄露汤底或核心答案。",
                "2) 玩家提问时，只能回答“是/否/无关/不确定”之一；如问题不是是非问，回复“请用是/否问题”。",
                "3) 玩家作最终推理时，仅判断对错，回答“正确”或“不正确”。",
                "4) 若提问次数已用完，只能提示玩家做最终推理。",
                "5) 仅在玩家明确请求提示时，且允许提示时，才可给出简短提示；提示不得包含汤底关键名词。",
                "",
                f"汤面：{self.config.surface}",
                f"汤底：{self.config.bottom}",
                f"任务目标：{self.config.objective}",
                f"提问次数上限：{self.config.max_questions}",
                f"剩余提问次数：{remaining}",
                f"允许提示：{self.config.allow_hints}",
                f"提示列表：{hints_text}",
                "",
                "请只输出JSON，格式如下：",
                '{"type":"question_response|final_guess_eval|control","reply":"...","is_correct":true/false,"end_game":true/false,"question_counted":true/false}',
            ]
        )

    def _normalize_endpoint(self) -> str:
        endpoint = self.base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions"
        return endpoint

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": True,
        }
        endpoint = self._normalize_endpoint()

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=True,
                )
                if response.status_code >= 400:
                    details = response.text.strip()
                    if response.status_code in {429, 500, 502, 503, 504}:
                        if attempt < self.max_retries:
                            time.sleep(self.retry_backoff * (2 ** (attempt - 1)))
                            continue
                    raise RuntimeError(
                        f"模型请求失败({response.status_code}): {details}"
                    )
                return self._read_stream(response)
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"网络错误: {exc}") from exc
                time.sleep(self.retry_backoff * (2 ** (attempt - 1)))

        raise RuntimeError("模型请求失败：重试次数已用完")

    def _read_stream(self, response: requests.Response) -> str:
        content_parts: List[str] = []
        for line in response.iter_lines():
            line = line.decode('utf-8')
            if not line:
                continue
            if not line.startswith("data:"):
                continue
            data_str = line[len("data:") :].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta") or choice.get("message") or {}
            piece = delta.get("content")
            if piece:
                content_parts.append(piece)
        return "".join(content_parts).strip()

    @staticmethod
    def safe_json_load(text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def sanitize_reply(reply: str, config: SoupConfig) -> str:
        if config.bottom and config.bottom in reply:
            return "不能直接揭示答案，请继续提问。"
        return reply

    @staticmethod
    def normalize_short_answer(reply: str) -> str:
        if reply in ALLOWED_SHORT_ANSWERS:
            return reply
        for item in ALLOWED_SHORT_ANSWERS:
            if item in reply:
                return item
        return "不确定"

    @staticmethod
    def is_hint_request(user_text: str) -> bool:
        markers = ["提示", "线索", "给点", "给个", "hint"]
        return any(m in user_text for m in markers)

    def handle_turn(self, user_text: str) -> str:
        if self.state.ended:
            return "游戏已结束。"

        if self.state.questions_asked >= self.config.max_questions:
            return "提问次数已用完，请进行最终推理。"

        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}] + self.history + [
            {"role": "user", "content": user_text}
        ]
        try:
            raw = self._call_llm(messages)
        except RuntimeError as exc:
            return str(exc)

        parsed = self.safe_json_load(raw)
        if not parsed:
            return ASK_YES_NO

        reply = self.sanitize_reply(str(parsed.get("reply", "")).strip(), self.config)
        reply_type = parsed.get("type")
        is_correct = bool(parsed.get("is_correct"))
        end_game = bool(parsed.get("end_game"))
        question_counted = bool(parsed.get("question_counted", True))

        if reply_type == "final_guess_eval":
            if is_correct:
                self.state.ended = True
                return "正确"
            if end_game:
                self.state.ended = True
                return "不正确，游戏结束。"
            return "不正确"

        if reply_type == "control" and self.is_hint_request(user_text):
            if self.config.allow_hints and self.config.hints:
                return self.config.hints[
                    min(self.state.questions_asked, len(self.config.hints) - 1)
                ]
            return "目前不提供提示。"

        if reply_type == "question_response":
            if question_counted:
                self.state.questions_asked += 1
            if reply == ASK_YES_NO:
                return reply
            return self.normalize_short_answer(reply)

        return ASK_YES_NO

    def record_turn(self, user_text: str, reply: str) -> None:
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})

    def run_cli(self) -> int:
        print("海龟汤主持人已就绪。")
        if self.config.title:
            print(f"汤名：{self.config.title}")
        print(f"汤面：{self.config.surface}")
        print(f"任务目标：{self.config.objective}")
        print(f"提问次数上限：{self.config.max_questions}")

        while True:
            try:
                user_text = input("玩家> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n退出游戏。")
                break
            if not user_text:
                continue
            if user_text in {"退出", "quit", "exit"}:
                print("退出游戏。")
                break
            reply = self.handle_turn(user_text)
            self.record_turn(user_text, reply)
            print(f"主持人> {reply}")
            if self.state.ended:
                break
        return 0
    def get_current_soup_info(self) -> Dict[str, Any]:
        remaining = max(self.config.max_questions - self.state.questions_asked, 0)
        return {
            "title": self.config.title,
            "surface": self.config.surface,
            "objective": self.config.objective,
            "max_questions": self.config.max_questions,
            "questions_asked": self.state.questions_asked,
            "remaining_questions": remaining,
            "allow_hints": self.config.allow_hints,
            "hints": list(self.config.hints),
            "ended": self.state.ended,
        }

    def get_soup_bottom(self) -> str:
        return self.config.bottom

    def get_current_soup_info_text(self) -> str:
        remaining = max(self.config.max_questions - self.state.questions_asked, 0)
        title = self.config.title or "未命名"
        return (
            f"汤名：{title}\n"
            f"汤面：{self.config.surface}\n"
            f"任务目标：{self.config.objective}\n"
            f"提问次数上限：{self.config.max_questions}\n"
            f"已提问：{self.state.questions_asked}\n"
            f"允许提示：{self.config.allow_hints}\n"
            "提问方法：触发词+#ask_soup提问内容"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="海龟汤主持人AI")
    parser.add_argument("--config", default=os.getenv("SOUP_CONFIG", DEFAULT_CONFIG))
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL", DEFAULT_API_BASE))
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY", random.choice(DEFAULT_API_KEY_LIST)))
    parser.add_argument("--soup", default=None, help="指定 soup id/title/name")
    parser.add_argument("--soup-index", type=int, default=None, help="指定第几个汤（1开始）")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    host = TurtleSoupHost(
        config_path=args.config,
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        soup_id=args.soup,
        soup_index=args.soup_index,
        max_retries=args.retries,
    )
    return host.run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
