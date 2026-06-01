"""古籍查询模块 - 六十日用法口诀、穷通宝鉴、三命通会、十二时辰吉凶。"""

from __future__ import annotations

from .data.datas import DAY_60, JIAN_CHU, SHI_CHEN_12
from .data.ganzhi import DI_ZHI
from .data.sizi import SUMMARY
from .data.yue import MONTH


class ReferenceTexts:
    """古籍文本查询器。"""

    def __init__(self, me: str, zhis: tuple, zhus: list):
        self.me = me
        self.zhis = zhis
        self.zhus = zhus

    def get_all(self) -> dict:
        """获取所有古籍查询结果。"""
        return {
            '六十日用法口诀': self.get_days60(),
            '穷通宝鉴': self.get_qiongtong(),
            '三命通会': self.get_sanming(),
            '十二时辰吉凶': self.get_shichen(),
        }

    def get_days60(self) -> str:
        """六十日用法口诀。"""
        key = self.me + self.zhis[2]
        return DAY_60.get(key, '')

    def get_qiongtong(self) -> str:
        """穷通宝鉴。"""
        key = self.me + self.zhis[1]
        return MONTH.get(key, '')

    def get_sanming(self) -> str:
        """三命通会。"""
        key = ''.join([self.me, '日', *self.zhus[3]])
        return SUMMARY.get(key, '')

    def get_shichen(self) -> str:
        """十二时辰（初中末）出生吉凶。"""
        return SHI_CHEN_12.get(self.zhis[3], '')

    def get_jianchu(self) -> dict:
        """建除。"""
        seq = 12 - DI_ZHI.index(self.zhis[1])
        idx = (DI_ZHI.index(self.zhis[2]) + seq) % 12
        name, desc = JIAN_CHU[idx]
        return {'name': name, 'desc': desc}
