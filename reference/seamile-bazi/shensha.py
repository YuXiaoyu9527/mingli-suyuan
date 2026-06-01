"""神煞计算模块。"""

from __future__ import annotations

from .data.datas import (
    SHEN_SHA_INFO,
    day_shens,
    g_shens,
    month_shens,
    year_shens,
)


class ShenShaCalculator:
    """神煞计算器。"""

    def __init__(
        self,
        me: str,
        gans: tuple,
        zhis: tuple,
    ):
        self.me = me
        self.gans = gans
        self.zhis = zhis

    def calc_all(self) -> dict:
        """计算所有神煞。

        返回按分类分组的字典：
        {
            "年支神煞": [{name, position, zhi, info}, ...],
            "月支神煞": [{name, matched, info}, ...],
            "日支神煞": [{name, position, zhi, info}, ...],
            "日主神煞": [{name, positions, info}, ...],
        }
        """
        result = {
            '年支神煞': self._calc_year_shens(),
            '月支神煞': self._calc_month_shens(),
            '日支神煞': self._calc_day_shens(),
            '日主神煞': self._calc_gan_shens(),
        }
        return result

    def _calc_year_shens(self) -> list[dict]:
        """基于年支的神煞。"""
        items = []
        year_zhi = self.zhis[0]
        positions = ['年', '月', '日', '时']

        for shen_name, table in year_shens.items():
            target = table.get(year_zhi, '')
            for seq, zhi in enumerate(self.zhis):
                if zhi in target:
                    items.append({
                        'name': shen_name,
                        'position': positions[seq],
                        'zhi': zhi,
                        'info': SHEN_SHA_INFO.get(shen_name, ''),
                    })
        return items

    def _calc_month_shens(self) -> list[dict]:
        """基于月支的神煞。"""
        items = []
        month_zhi = self.zhis[1]

        for shen_name, table in month_shens.items():
            target = table.get(month_zhi, '')
            # 天德、月德可以匹配天干和地支
            matched_positions = []
            for seq, g in enumerate(self.gans):
                pos = ['年', '月', '日', '时'][seq]
                if g == target:
                    matched_positions.append(pos + '干' + g)
            for seq, z in enumerate(self.zhis):
                pos = ['年', '月', '日', '时'][seq]
                if z == target:
                    matched_positions.append(pos + '支' + z)

            if matched_positions:
                items.append({
                    'name': shen_name,
                    'matched': matched_positions,
                    'info': SHEN_SHA_INFO.get(shen_name, ''),
                })
        return items

    def _calc_day_shens(self) -> list[dict]:
        """基于日支的神煞。"""
        items = []
        day_zhi = self.zhis[2]
        positions = ['年', '月', '日', '时']

        for shen_name, table in day_shens.items():
            target = table.get(day_zhi, '')
            for seq, zhi in enumerate(self.zhis):
                if seq == 2:
                    continue
                if zhi == target:
                    items.append({
                        'name': shen_name,
                        'position': positions[seq],
                        'zhi': zhi,
                        'info': SHEN_SHA_INFO.get(shen_name, ''),
                    })
        return items

    def _calc_gan_shens(self) -> list[dict]:
        """基于日主的神煞。"""
        items = []
        me = self.me

        for shen_name, table in g_shens.items():
            target = table.get(me, '')
            if not target:
                continue
            matched_positions = []
            for seq, zhi in enumerate(self.zhis):
                pos = ['年', '月', '日', '时'][seq]
                if zhi in target:
                    matched_positions.append(pos + '支' + zhi)

            if matched_positions:
                items.append({
                    'name': shen_name,
                    'positions': matched_positions,
                    'info': SHEN_SHA_INFO.get(shen_name, ''),
                })
        return items

    def get_shens_for_zhu(
        self,
        gans: tuple | list,
        zhis: tuple | list,
        extra_gan: str,
        extra_zhi: str,
    ) -> list[str]:
        """为大运/流年计算匹配的神煞。"""
        result = []
        me = self.me
        year_zhi = zhis[0]
        day_zhi = zhis[2]

        for shen_name, table in year_shens.items():
            target = table.get(year_zhi, '')
            if extra_zhi in target:
                result.append(shen_name)

        for shen_name, table in day_shens.items():
            target = table.get(day_zhi, '')
            if extra_zhi == target:
                result.append(shen_name)

        for shen_name, table in g_shens.items():
            target = table.get(me, '')
            if extra_zhi in target:
                result.append(shen_name)

        return result
