from dataclasses import asdict, dataclass
import os
from typing import List, Optional
import requests



@dataclass
class IndexTTS2RequestData:
    text: str
    spk_audio_path: str
    emo_control_method: int = 0
    emo_ref_path: Optional[str] = None
    emo_weight: float = 1.0
    emo_vec: List[float] = None
    emo_text: Optional[str] = None
    emo_random: bool = False
    max_text_tokens_per_sentence: int = 120

    def __post_init__(self):
        # 保证 emo_vec 默认长度为 8 的 0 向量
        if self.emo_vec is None:
            self.emo_vec = [0.0] * 8

    def to_dict(self) -> str:
        return asdict(self)