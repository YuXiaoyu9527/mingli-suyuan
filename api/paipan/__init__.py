"""
排盘引擎 - 公开API
=================

使用示例:
    from api.paipan import paipan, to_dict

    result = paipan(1990, 5, 20, 14, 30, gender="男")
    data = to_dict(result)
    print(data["pillars"]["day"]["ganzhi"])  # 日柱干支
"""

from .engine import paipan, to_dict, BaziResult, Pillar
from .dayun import calc_dayun, calc_dayun_from_lunar
from .shensha import calc_shensha

__all__ = [
    "paipan",
    "to_dict",
    "BaziResult",
    "Pillar",
    "calc_dayun",
    "calc_dayun_from_lunar",
    "calc_shensha",
]
