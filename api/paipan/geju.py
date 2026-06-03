"""
格局自动判定引擎
================
从八字自动识别正格和变格。

正格: 以月令藏干主气对日主的十神来定
变格: 专旺格/从格

用法:
  from api.paipan.geju import GejuEngine
  engine = GejuEngine()
  result = engine.determine(bazi)
"""

from dataclasses import dataclass, field
from .data.ganzhi import (
    ZHI_CANGGAN, ZHI_MAIN_QI, TIAN_GAN, DI_ZHI,
    GAN_WUXING, ZHI_WUXING, get_shishen,
)


@dataclass
class GejuResult:
    """格局判定结果"""
    pattern: str           # 格局名称
    pattern_type: str      # "正格" / "变格" / "从格"
    yueling: str           # 月令藏干主气
    yueling_shishen: str   # 月令对日主的十神
    is_chengge: bool       # 是否成格
    chengge_conditions: list = field(default_factory=list)  # 成格条件
    baige_reasons: list = field(default_factory=list)       # 败格原因
    analysis: str = ""     # 分析文本


class GejuEngine:
    """格局判定引擎"""

    def determine(self, bazi) -> GejuResult:
        """主入口：判定八字格局"""
        rizhu = bazi.rizhu
        month_zhi = bazi.month.zhi
        month_main_qi = ZHI_MAIN_QI.get(month_zhi, "")
        yueling_shishen = get_shishen(rizhu, month_main_qi)

        # 1. 先检查是否为变格（专旺/从格）
        special = self._check_special(bazi)
        if special:
            return special

        # 2. 正格判定
        return self._determine_zhengge(bazi, month_main_qi, yueling_shishen)

    def _check_special(self, bazi) -> GejuResult | None:
        """检查是否为变格"""
        rizhu = bazi.rizhu
        scores = bazi.wuxing_scores
        rizhu_wx = GAN_WUXING[rizhu]
        total = sum(scores.values())

        # 检查专旺格：某一行占绝对优势(>60%)
        for wx, score in scores.items():
            if score > total * 0.6 and wx == rizhu_wx:
                return self._check_zhuanwang(bazi, wx)

        # 检查从格：日主极弱(<15%)，被某一五行克制
        if scores[rizhu_wx] < total * 0.15:
            return self._check_congge(bazi, rizhu_wx, scores)

        return None

    def _check_zhuanwang(self, bazi, wx: str) -> GejuResult | None:
        """检查专旺格"""
        # 地支是否成局
        zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
        wx_zhis = [z for z in zhis if ZHI_WUXING.get(z) == wx]

        ZHUANWANG_MAP = {
            "木": ("曲直格", "木"),
            "火": ("炎上格", "火"),
            "土": ("稼穑格", "土"),
            "金": ("从革格", "金"),
            "水": ("润下格", "水"),
        }

        if wx in ZHUANWANG_MAP and len(wx_zhis) >= 3:
            name, element = ZHUANWANG_MAP[wx]
            return GejuResult(
                pattern=name,
                pattern_type="变格",
                yueling=ZHI_MAIN_QI.get(bazi.month.zhi, ""),
                yueling_shishen=get_shishen(bazi.rizhu, ZHI_MAIN_QI.get(bazi.month.zhi, "")),
                is_chengge=len(wx_zhis) >= 3,
                chengge_conditions=[f"地支{wx_zhis}均为{wx}，{wx}气专旺"],
                analysis=f"此为{element}之专旺格。{name}者，{element}气纯粹，"
                        f"命主性格鲜明，运势随{element}气消长。"
                        f"宜行{element}运，忌官杀克制。",
            )

        return None

    def _check_congge(self, bazi, rizhu_wx: str, scores: dict) -> GejuResult | None:
        """检查从格"""
        # 找最强的五行
        strongest_wx = max(scores, key=scores.get)
        if strongest_wx == rizhu_wx:
            return None  # 自己最强，不可能是从格

        WUXING_SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
        WUXING_KE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}

        cong_name = ""
        # 从杀格：官杀极旺
        ke_rizhu = WUXING_KE.get(
            next((k for k, v in WUXING_KE.items() if v == rizhu_wx), ""), ""
        )
        if ke_rizhu and scores.get(ke_rizhu, 0) > sum(scores.values()) * 0.5:
            cong_name = "从杀格"
        # 从财格：财星极旺
        elif rizhu_wx in WUXING_KE:
            bei_ke = WUXING_KE[rizhu_wx]
            if scores.get(bei_ke, 0) > sum(scores.values()) * 0.5:
                cong_name = "从财格"
        # 从儿格：食伤极旺
        elif rizhu_wx in WUXING_SHENG:
            wo_sheng = WUXING_SHENG[rizhu_wx]
            if scores.get(wo_sheng, 0) > sum(scores.values()) * 0.5:
                cong_name = "从儿格"

        if cong_name:
            return GejuResult(
                pattern=cong_name,
                pattern_type="从格",
                yueling=ZHI_MAIN_QI.get(bazi.month.zhi, ""),
                yueling_shishen=get_shishen(bazi.rizhu, ZHI_MAIN_QI.get(bazi.month.zhi, "")),
                is_chengge=True,
                chengge_conditions=[f"日主{rizhu_wx}极弱，全局{strongest_wx}旺，不得不从"],
                analysis=f"此为{cong_name}。日主极弱，弃命从强。"
                        f"宜顺从旺势而行，不宜逆势而为。",
            )

        return None

    def _determine_zhengge(self, bazi, month_qi: str, yueling_ss: str) -> GejuResult:
        """判定正格"""
        rizhu = bazi.rizhu

        # 月令十神 → 格局名
        ZHENGGE_MAP = {
            "正官": "正官格", "七杀": "七杀格",
            "正财": "正财格", "偏财": "偏财格",
            "正印": "正印格", "偏印": "偏印格",
            "食神": "食神格", "伤官": "伤官格",
        }

        pattern = ZHENGGE_MAP.get(yueling_ss, "")

        # 特殊情况：建禄格/羊刃格（月令与日主同五行）
        if not pattern:
            from .data.ganzhi import is_yang
            if GAN_WUXING[rizhu] == ZHI_WUXING[bazi.month.zhi]:
                # 日主同五行 → 建禄或羊刃
                if is_yang(rizhu):
                    pattern = "羊刃格"
                else:
                    pattern = "建禄格"

        if not pattern:
            pattern = f"{yueling_ss}格" if yueling_ss else "无格"

        # 检查成格/败格条件
        conditions = []
        reasons = []

        # 通用成格条件：日主有根气
        rizhu_scores = bazi.wuxing_scores.get(GAN_WUXING[rizhu], 0)
        total = sum(bazi.wuxing_scores.values())
        if rizhu_scores < total * 0.1:
            reasons.append("日主无根气，格局不真")
        else:
            conditions.append("日主有根")

        # 正官格：不宜见伤官
        if pattern == "正官格":
            shishen_count = bazi.shishen_count
            if shishen_count.get("伤官", 0) > 0:
                reasons.append("正官格见伤官，官星被伤")
            if shishen_count.get("七杀", 0) > 0:
                reasons.append("官杀混杂")
            if not reasons:
                conditions.append("正官清纯无伤")

        # 七杀格：宜有制化
        if pattern == "七杀格":
            shishen_count = bazi.shishen_count
            if shishen_count.get("食神", 0) > 0:
                conditions.append("七杀有食神制")
            elif shishen_count.get("正印", 0) > 0:
                conditions.append("七杀有印化")
            else:
                reasons.append("七杀无制，格局欠佳")

        is_chengge = len(conditions) > len(reasons)

        return GejuResult(
            pattern=pattern,
            pattern_type="正格",
            yueling=month_qi,
            yueling_shishen=yueling_ss,
            is_chengge=is_chengge,
            chengge_conditions=conditions,
            baige_reasons=reasons,
            analysis=self._gen_analysis(pattern, yueling_ss, conditions, reasons),
        )

    def _gen_analysis(self, pattern, yueling_ss, conditions, reasons) -> str:
        """生成格局分析"""
        parts = [f"月令藏干主气对日主为{yueling_ss}，入{pattern}。"]

        if conditions:
            parts.append(f"成格条件：{'；'.join(conditions)}。")
        if reasons:
            parts.append(f"败格因素：{'；'.join(reasons)}。")

        if not reasons:
            parts.append("格局清纯，按正格论命。")
        else:
            parts.append("格局有瑕，需结合大运流年看格局变化。")

        return "".join(parts)
