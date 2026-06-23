"""
AI 解读器
=========
连接 DeepSeek-V4 API（OpenAI 兼容接口）。
AI只解读/教学，不碰排盘计算。

配置：在项目根目录创建 .env 文件
  DEEPSEEK_API_KEY=your_key_here
  DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
"""

import os
import json
from pathlib import Path
from typing import Optional

from .prompts import (
    build_jianpi_prompt,
    build_daily_yiji_prompt,
    build_mentor_prompt,
    build_qa_prompt,
)

# ===== 配置 =====
ROOT = Path(__file__).parent.parent.parent
ENV_FILE = ROOT / ".env"

# 尝试加载 .env
if ENV_FILE.exists():
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


class AIInterpreter:
    """AI解读器 - 封装 DeepSeek API 调用"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self._client = None

    @property
    def client(self):
        """延迟初始化 OpenAI 客户端"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    def _call(self, system_content: str, user_content: str, max_tokens: int = 800) -> str:
        """调用LLM"""
        if not self.api_key:
            return (
                "【AI未配置】\n请在项目根目录创建 .env 文件，添加：\n"
                "DEEPSEEK_API_KEY=你的API密钥\n\n"
                "获取密钥：https://platform.deepseek.com"
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"【AI调用失败】{e}\n请检查API密钥和网络连接。"

    # ===== 公开方法 =====

    def jianpi(
        self,
        paipan_json: dict,
        ancient_refs: str,
    ) -> str:
        """
        八字简批。

        Args:
            paipan_json: 排盘引擎输出的JSON（Layer 2）
            ancient_refs: RAG检索到的古籍原文（Layer 3）
        """
        # 提取关键数据，去掉冗余
        key_data = {
            "八字": f"{paipan_json['pillars']['year']['ganzhi']} "
                    f"{paipan_json['pillars']['month']['ganzhi']} "
                    f"{paipan_json['pillars']['day']['ganzhi']} "
                    f"{paipan_json['pillars']['hour']['ganzhi']}",
            "日主": f"{paipan_json['rizhu']}({paipan_json['rizhu_wuxing']})",
            "五行分数": paipan_json.get("wuxing_scores", {}),
            "十神统计": paipan_json.get("shishen_count", {}),
            "日柱纳音": paipan_json['pillars']['day']['nayin'],
            "地支关系": paipan_json.get("zhi_relations", {}),
        }
        paipan_str = json.dumps(key_data, ensure_ascii=False, indent=2)

        prompt = build_jianpi_prompt(paipan_str, ancient_refs)
        return self._call(SYSTEM_ROLE.strip(), prompt, max_tokens=600)

    def jianpi_en(
        self,
        paipan_json: dict,
        ancient_refs: str,
    ) -> str:
        """English BaZi blueprint interpretation"""
        wx_en = {"金":"Metal","木":"Wood","水":"Water","火":"Fire","土":"Earth"}
        key_data = {
            "Four Pillars": (
                f"{paipan_json['pillars']['year']['ganzhi']} "
                f"{paipan_json['pillars']['month']['ganzhi']} "
                f"{paipan_json['pillars']['day']['ganzhi']} "
                f"{paipan_json['pillars']['hour']['ganzhi']}"
            ),
            "Day Master": f"{paipan_json['rizhu']} ({wx_en.get(paipan_json['rizhu_wuxing'], paipan_json['rizhu_wuxing'])})",
            "Element Scores": {wx_en.get(k,k): v for k,v in paipan_json.get("wuxing_scores", {}).items()},
            "Day Pillar Nayin": paipan_json['pillars']['day']['nayin'],
        }
        paipan_str = json.dumps(key_data, ensure_ascii=False, indent=2)

        en_system = (
            "You are a BaZi (Chinese Four Pillars) interpreter for a Western audience. "
            "Write in clear, engaging English. "
            "Explain what the user's Day Master element means for their personality, strengths, and life path. "
            "Use MBTI-like language and modern self-discovery framing. "
            "Avoid technical Chinese terms unless you explain them. "
            "Keep it warm, insightful, and under 250 words. "
            "Never make absolute predictions — use 'tends to', 'may', 'often'."
        )
        en_prompt = (
            "Based on this BaZi chart, write a 'Personal Element Blueprint' for the user:\n\n"
            f"{paipan_str}\n\n"
            "If ancient text references are available, incorporate them naturally:\n"
            f"{ancient_refs}\n\n"
            "Structure your response as:\n"
            "1. Your Element Type (1-2 sentences — e.g. 'You are a Wood person...')\n"
            "2. Personality & Strengths (3-4 bullet-like sentences)\n"
            "3. Life Path & Growth Areas (2-3 sentences)\n"
            "4. Ancient Wisdom Note (1 sentence connecting to classical Chinese text, if available)"
        )
        return self._call(en_system, en_prompt, max_tokens=600)

    def daily_yiji(
        self,
        day_ganzhi: str,
        day_info: dict,
        user_bazi_brief: str,
        ancient_refs: str,
    ) -> str:
        """今日宜忌解读"""
        info_str = json.dumps({
            "今日干支": day_ganzhi,
            "建除": day_info.get("jianshen", ""),
            "黄道黑道": day_info.get("huangdao", ""),
        }, ensure_ascii=False, indent=2)

        prompt = build_daily_yiji_prompt(info_str, user_bazi_brief, ancient_refs)
        return self._call(SYSTEM_ROLE.strip(), prompt, max_tokens=600)

    def mentor(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        ancient_refs: str,
    ) -> str:
        """断案录导师提示"""
        prompt = build_mentor_prompt(question, student_answer, correct_answer, ancient_refs)
        return self._call(SYSTEM_ROLE.strip(), prompt, max_tokens=500)

    def ask(
        self,
        question: str,
        ancient_refs: str,
    ) -> str:
        """通用问答"""
        prompt = build_qa_prompt(question, ancient_refs)
        return self._call(SYSTEM_ROLE.strip(), prompt, max_tokens=800)


# ===== 导出系统角色供外部使用 =====
from .prompts import SYSTEM_ROLE  # noqa: E402
