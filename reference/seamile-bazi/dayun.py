"""大运和流年计算模块。"""

from __future__ import annotations

from .data.datas import NA_YIN, day_shens, g_shens, year_shens
from .data.ganzhi import (
    CANG_GAN,
    DI_ZHI,
    GONG_HE,
    SHI_SHEN,
    ZHI_ATTR,
)
from .utils import check_gan, is_kong_wang, yinyang


class DaYunCalculator:
    """大运和流年计算器。"""

    def __init__(self, calculator):
        self.calc = calculator
        self.me = calculator.me
        self.gans = calculator.gans
        self.zhis = calculator.zhis
        self.zhus = calculator.zhus
        self.ba = calculator.ba
        self.lunar = calculator.lunar
        self.is_female = calculator.is_female

    def calc_dayun(self) -> list[dict]:
        """计算大运列表（不含流年详情）。"""
        if not self.ba:
            return self._calc_dayun_from_ganzhi()
        return self._calc_dayun_from_lunar()

    def calc_dayun_with_liunian(self) -> list[dict]:
        """计算大运（含流年详情）。"""
        if not self.ba:
            return self._calc_dayun_from_ganzhi()
        return self._calc_dayun_with_liunian_from_lunar()

    def _calc_dayun_from_ganzhi(self) -> list[dict]:
        """从干支序列计算大运（无法获取起始年龄和流年）。"""
        dayuns = self.calc.dayuns
        result = []
        for gz in dayuns:
            gan_ = gz[0]
            zhi_ = gz[1]
            result.append(self._make_dayun_item(gan_, zhi_))
        return result

    def _calc_dayun_from_lunar(self) -> list[dict]:
        """从 lunar 对象计算大运。"""
        yun = self.ba.getYun(0 if self.is_female else 1)
        result = []
        for dayun in yun.getDaYun()[1:]:
            gan_ = dayun.getGanZhi()[0]
            zhi_ = dayun.getGanZhi()[1]
            item = self._make_dayun_item(gan_, zhi_)
            item['start_age'] = dayun.getStartAge()
            result.append(item)
        return result

    def _calc_dayun_with_liunian_from_lunar(self) -> list[dict]:
        """从 lunar 对象计算大运（含流年）。"""
        yun = self.ba.getYun(0 if self.is_female else 1)
        result = []
        for dayun in yun.getDaYun()[1:]:
            gan_ = dayun.getGanZhi()[0]
            zhi_ = dayun.getGanZhi()[1]
            item = self._make_dayun_item(gan_, zhi_)
            item['start_age'] = dayun.getStartAge()

            # 流年
            liunians = []
            zhis2 = [*list(self.zhis), zhi_]
            gans2 = [*list(self.gans), gan_]
            for liunian in dayun.getLiuNian():
                ln_item = self._make_liunian_item(liunian, gans2, zhis2)
                liunians.append(ln_item)
            item['liunian'] = liunians
            result.append(item)
        return result

    def _make_dayun_item(self, gan_: str, zhi_: str) -> dict:
        """构建大运数据项。"""
        me = self.me
        day_zhu = self.zhus[2]

        # 地支藏干
        zhi5_ = [{'gan': gan, 'shishen': SHI_SHEN[me][gan]} for gan in CANG_GAN[zhi_]]

        # 地支关系
        zhi_rels = set()
        for item in self.zhis:
            for type_ in ZHI_ATTR[zhi_]:
                target = ZHI_ATTR[zhi_][type_]
                if isinstance(target, str):
                    if item == target:
                        zhi_rels.add(f'{type_}:{item}')
                elif isinstance(target, tuple):
                    if item in target:
                        zhi_rels.add(f'{type_}:{item}')

        # 与命局天干同名的夹
        jia = self._calc_jia(gan_, zhi_, self.gans, self.zhis, 4)

        # 神煞
        shens = self._calc_shens_for_extra(gan_, zhi_)

        # 重复柱标记
        fu = (gan_, zhi_) in self.zhus

        return {
            'ganzhi': gan_ + zhi_,
            'gan': gan_,
            'zhi': zhi_,
            'gan_shishen': SHI_SHEN[me][gan_],
            'zhi_shishen': SHI_SHEN[me][zhi_],
            'zhi_canggan': zhi5_,
            'nayin': NA_YIN.get((gan_, zhi_), ''),
            'gan_relations': check_gan(gan_, self.gans),
            'zhi_relations': sorted(zhi_rels),
            'kong_wang': is_kong_wang(day_zhu, zhi_),
            'jia': jia,
            'shens': shens,
            'repeat': fu,
            'gan_yinyang': yinyang(gan_),
            'zhi_yinyang': yinyang(zhi_),
        }

    def _make_liunian_item(self, liunian, gans2: list, zhis2: list) -> dict:  # noqa: C901
        """构建流年数据项。"""
        me = self.me
        day_zhu = self.zhus[2]

        gan2_ = liunian.getGanZhi()[0]
        zhi2_ = liunian.getGanZhi()[1]

        # 地支藏干
        zhi6_ = [{'gan': gan, 'shishen': SHI_SHEN[me][gan]} for gan in CANG_GAN[zhi2_]]

        # 地支关系（与五柱）
        zhi_rels = set()
        for item in zhis2:
            for type_ in ZHI_ATTR[zhi2_]:
                if type_ == '破':
                    continue
                target = ZHI_ATTR[zhi2_][type_]
                if isinstance(target, str):
                    if item == target:
                        zhi_rels.add(f'{type_}:{item}')
                elif isinstance(target, tuple):
                    if item in target:
                        zhi_rels.add(f'{type_}:{item}')

        # 夹
        jia = self._calc_jia(gan2_, zhi2_, gans2, zhis2, 5)

        # 拱
        gong_items = []
        if gan2_ in gans2:
            for i in range(5):
                if gan2_ == gans2[i]:
                    zhi1 = zhis2[i]
                    if zhi1 + zhi2_ in GONG_HE:
                        if GONG_HE[zhi1 + zhi2_] not in self.zhis:
                            gong_items.append(GONG_HE[zhi1 + zhi2_])

        # 神煞
        shens = self._calc_shens_for_extra(gan2_, zhi2_)

        # 特殊局（四生、四败、四库等）
        specials = self._calc_specials(zhis2, zhi2_)

        # 重复柱
        fu = (gan2_, zhi2_) in self.zhus

        return {
            'age': liunian.getAge(),
            'year': liunian.getYear(),
            'ganzhi': gan2_ + zhi2_,
            'gan': gan2_,
            'zhi': zhi2_,
            'gan_shishen': SHI_SHEN[me][gan2_],
            'zhi_shishen': SHI_SHEN[me][zhi2_],
            'zhi_canggan': zhi6_,
            'nayin': NA_YIN.get((gan2_, zhi2_), ''),
            'gan_relations': check_gan(gan2_, gans2),
            'zhi_relations': sorted(zhi_rels),
            'kong_wang': is_kong_wang(day_zhu, zhi2_),
            'jia': jia,
            'gong': gong_items,
            'shens': shens,
            'specials': specials,
            'repeat': fu,
            'gan_yinyang': yinyang(gan2_),
            'zhi_yinyang': yinyang(zhi2_),
        }

    def _calc_jia(self, gan_: str, zhi_: str, gans: tuple | list, zhis: tuple | list, count: int) -> list[str]:
        """计算夹合。"""
        jia = []
        if gan_ in gans:
            for i in range(count):
                if i >= len(gans):
                    break
                if gan_ == gans[i]:
                    diff = abs(
                        DI_ZHI.index(zhi_) - DI_ZHI.index(zhis[i]),
                    )
                    if diff == 2:
                        mid = DI_ZHI[(DI_ZHI.index(zhi_) + DI_ZHI.index(zhis[i])) // 2]
                        jia.append(f'夹：{mid}')
                    if diff == 10:
                        mid = DI_ZHI[(DI_ZHI.index(zhi_) + DI_ZHI.index(zhis[i])) % 12]
                        jia.append(f'夹：{mid}')
        return jia

    def _calc_shens_for_extra(self, gan_: str, zhi_: str) -> list[str]:
        """为大运/流年计算神煞（简化版）。"""
        result = []
        year_zhi = self.zhis[0]
        day_zhi = self.zhis[2]

        for shen_name, table in year_shens.items():
            target = table.get(year_zhi, '')
            if zhi_ in target:
                result.append(shen_name)

        for shen_name, table in day_shens.items():
            target = table.get(day_zhi, '')
            if zhi_ == target:
                result.append(shen_name)

        for shen_name, table in g_shens.items():
            target = table.get(self.me, '')
            if zhi_ in target:
                result.append(shen_name)

        return result

    def _calc_specials(
        self,
        zhis2: list,
        zhi2_: str,
    ) -> list[str]:
        """计算流年特殊组合（天罗地网、四生、四败、四库）。"""
        specials = []
        all_zhis = set(zhis2) | {zhi2_}
        if {'戌', '亥', '辰', '巳'}.issubset(all_zhis):
            specials.append('天罗地网：戌亥辰巳')
        if {'寅', '申', '巳', '亥'}.issubset(all_zhis) and len(
            {'寅', '申', '巳', '亥'} & set(self.zhis),
        ) == 2:
            specials.append('四生：寅申巳亥')
        if {'子', '午', '卯', '酉'}.issubset(all_zhis) and len(
            {'子', '午', '卯', '酉'} & set(self.zhis),
        ) == 2:
            specials.append('四败：子午卯酉')
        if {'辰', '戌', '丑', '未'}.issubset(all_zhis) and len(
            {'辰', '戌', '丑', '未'} & set(self.zhis),
        ) == 2:
            specials.append('四库：辰戌丑未')
        return specials
