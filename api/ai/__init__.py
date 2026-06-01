"""
AI 解读层 - DeepSeek API 集成

用法:
  from api.ai import AIInterpreter
  ai = AIInterpreter(api_key="your-key")
  result = ai.jianpi(paipan_json, ancient_refs)
"""

from .interpreter import AIInterpreter
from .prompts import SYSTEM_ROLE

__all__ = ["AIInterpreter", "SYSTEM_ROLE"]
