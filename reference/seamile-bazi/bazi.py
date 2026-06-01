"""BaZi 八字排盘核心类。"""

from __future__ import annotations

import json

from .analyzer import Analyzer
from .calculator import (
    Calculator,
    FourPillars,
    create_from_bazi,
    create_from_lunar,
    create_from_solar,
)
from .data.datas import MING_GONG
from .dayun import DaYunCalculator
from .reference import ReferenceTexts
from .shensha import ShenShaCalculator


class BaZi:
    """八字排盘核心类。

    提供三种创建方式和多种分析方法，
    所有结果可以 dict 或 json 格式返回。
    """

    def __init__(
        self,
        pillars: FourPillars,
        is_female: bool,
        solar_obj=None,
        lunar_obj=None,
        ba_obj=None,
    ):
        self._is_female = is_female
        self._solar = solar_obj
        self._lunar = lunar_obj
        self._ba = ba_obj

        # 核心计算引擎
        self._calc = Calculator(
            pillars,
            is_female,
            solar_obj,
            lunar_obj,
            ba_obj,
        )

        # 分析引擎（延迟初始化）
        self._analyzer = None
        self._shensha = None
        self._dayun_calc = None
        self._reference = None

    # ── 三种构造方式 ──────────────────────────────────

    @classmethod
    def from_solar(
        cls,
        sex: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        tz: int = 8,
    ) -> BaZi:
        """通过公历日期创建。

        Args:
            sex: "男" 或 "女"
            year: 公历年
            month: 公历月
            day: 公历日
            hour: 时辰（0-23）
            tz: 时区，默认东八区
        """
        is_female = sex == '女'
        pillars, solar, lunar, ba = create_from_solar(
            year,
            month,
            day,
            hour,
            tz,
        )
        return cls(pillars, is_female, solar, lunar, ba)

    @classmethod
    def from_lunar(
        cls,
        sex: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        tz: int = 8,
        is_leap_month: bool = False,
    ) -> BaZi:
        """通过农历日期创建。

        Args:
            sex: "男" 或 "女"
            year: 农历年
            month: 农历月
            day: 农历日
            hour: 时辰（0-23）
            tz: 时区，默认东八区
            is_leap_month: 是否闰月
        """
        is_female = sex == '女'
        pillars, solar, lunar, ba = create_from_lunar(
            year,
            month,
            day,
            hour,
            tz,
            is_leap_month,
        )
        return cls(pillars, is_female, solar, lunar, ba)

    @classmethod
    def from_bazi(
        cls,
        sex: str,
        year_gz: str,
        month_gz: str,
        day_gz: str,
        time_gz: str,
    ) -> BaZi:
        """通过八字干支直接创建。

        Args:
            sex: "男" 或 "女"
            year_gz: 年柱干支，如 "丙寅"
            month_gz: 月柱干支，如 "戊戌"
            day_gz: 日柱干支，如 "丙戌"
            time_gz: 时柱干支，如 "乙未"
        """
        is_female = sex == '女'
        pillars, solar, lunar, ba = create_from_bazi(
            year_gz,
            month_gz,
            day_gz,
            time_gz,
        )
        return cls(pillars, is_female, solar, lunar, ba)

    # ── 延迟初始化 ────────────────────────────────────

    @property
    def analyzer(self) -> Analyzer:
        if self._analyzer is None:
            self._analyzer = Analyzer(self._calc)
        return self._analyzer

    @property
    def shensha_calc(self) -> ShenShaCalculator:
        if self._shensha is None:
            self._shensha = ShenShaCalculator(
                self._calc.me,
                self._calc.gans,
                self._calc.zhis,
            )
        return self._shensha

    @property
    def dayun_calculator(self) -> DaYunCalculator:
        if self._dayun_calc is None:
            self._dayun_calc = DaYunCalculator(self._calc)
        return self._dayun_calc

    @property
    def reference(self) -> ReferenceTexts:
        if self._reference is None:
            self._reference = ReferenceTexts(
                self._calc.me,
                self._calc.zhis,
                self._calc.zhus,
            )
        return self._reference

    # ── 基础信息方法 ──────────────────────────────────

    def basic_info(self) -> dict:
        """基础信息。"""
        calc = self._calc
        result = {
            'sex': '女' if self._is_female else '男',
            'four_pillars': {
                'year': {'gan': calc.gans[0], 'zhi': calc.zhis[0]},
                'month': {'gan': calc.gans[1], 'zhi': calc.zhis[1]},
                'day': {'gan': calc.gans[2], 'zhi': calc.zhis[2]},
                'time': {'gan': calc.gans[3], 'zhi': calc.zhis[3]},
            },
            'four_ganzhi': calc.pillars.four_ganzhi,
            'day_master': calc.me,
        }

        if self._solar:
            result['solar'] = {
                'year': self._solar.getYear(),
                'month': self._solar.getMonth(),
                'day': self._solar.getDay(),
            }
        if self._lunar:
            result['lunar'] = {
                'year': self._lunar.getYear(),
                'month': self._lunar.getMonth(),
                'day': self._lunar.getDay(),
            }
            # 命宫、胎元、身宫
            if self._ba:
                mg = self._ba.getMingGong()
                result['ming_gong'] = mg
                result['ming_gong_desc'] = MING_GONG.get(mg[1], '')
                result['tai_yuan'] = self._ba.getTaiYuan()
                result['shen_gong'] = self._ba.getShenGong()

            # 星宿
            result['xingxiu'] = {
                'name': self._lunar.getXiu(),
                'song': self._lunar.getXiuSong(),
            }

            # 上运信息
            if self._ba:
                yun = self._ba.getYun(0 if self._is_female else 1)
                result['start_dayun'] = {
                    'year': yun.getStartYear(),
                    'month': yun.getStartMonth(),
                    'day': yun.getStartDay(),
                }

        return result

    def four_pillars(self) -> dict:
        """四柱详细信息。"""
        pillars = [self._calc.get_pillar_detail(i) for i in range(4)]

        # 建除
        jianchu = self.reference.get_jianchu()

        return {
            'pillars': pillars,
            'jianchu': jianchu,
        }

    def wuxing_scores(self) -> dict:
        """五行分数和强弱信息。"""
        return self._calc.get_wuxing_scores()

    # ── 运势方法 ──────────────────────────────────────

    def dayun(self) -> list[dict]:
        """大运列表。"""
        return self.dayun_calculator.calc_dayun()

    def dayun_with_liunian(self) -> list[dict]:
        """大运与流年。"""
        return self.dayun_calculator.calc_dayun_with_liunian()

    # ── 分析方法 ──────────────────────────────────────

    def shensha(self) -> dict:
        """神煞分析。"""
        return self.shensha_calc.calc_all()

    def liuqin(self) -> dict:
        """六亲分析。"""
        return self._calc.get_liuqin()

    def zangfu(self) -> dict:
        """脏腑分析。"""
        return self._calc.get_zangfu()

    def geju(self) -> dict:
        """格局分析。"""
        return self.analyzer.get_geju()

    def analysis(self) -> dict:
        """命理分析。"""
        return {
            '十神分析': self.analyzer.get_shishen_analysis(),
            '特殊分析': self.analyzer.get_special_analysis(),
            '建禄格': self.analyzer.get_jianlu(),
            '拱合': self.analyzer.get_gong_analysis(),
        }

    def reference_texts(self) -> dict:
        """古籍查询。"""
        return self.reference.get_all()

    def special_stars(self) -> dict:
        """特殊星宿。"""
        return self.analyzer.get_special_stars()

    # ── 汇总方法 ──────────────────────────────────────

    def full_report(self) -> dict:
        """完整排盘结果。"""
        return {
            '基础信息': self.basic_info(),
            '四柱详情': self.four_pillars(),
            '五行分数': self.wuxing_scores(),
            '神煞': self.shensha(),
            '六亲': self.liuqin(),
            '脏腑': self.zangfu(),
            '格局': self.geju(),
            '命理分析': self.analysis(),
            '古籍查询': self.reference_texts(),
            '特殊星宿': self.special_stars(),
            '大运': self.dayun(),
        }

    # ── 序列化方法 ────────────────────────────────────

    def to_dict(self, section: str | None = None) -> dict:
        """以 dict 格式返回结果。"""
        if section is None:
            return self.full_report()

        method_map = {
            'basic': self.basic_info,
            'pillars': self.four_pillars,
            'wuxing': self.wuxing_scores,
            'dayun': self.dayun,
            'shensha': self.shensha,
            'liuqin': self.liuqin,
            'zangfu': self.zangfu,
            'geju': self.geju,
            'analysis': self.analysis,
            'reference': self.reference_texts,
            'stars': self.special_stars,
        }
        if section in method_map:
            return method_map[section]()
        msg = f'未知的 section: {section}'
        raise ValueError(msg)

    def to_json(
        self,
        section: str | None = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """以 JSON 字符串格式返回结果。"""
        data = self.to_dict(section)
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=str,
        )
