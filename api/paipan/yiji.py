"""
完整老黄历引擎
==============
基于 lunar_python 内置黄历数据 + 个人八字分析。

数据来源：
  - lunar_python (农历/干支/宜忌/神煞/方位/星宿) → 《协纪辨方书》体系
  - 个人维度：五行补缺 + 地支冲合 + 十神分析（算法）

用法:
  from api.paipan.yiji import DailyYiji
  yj = DailyYiji()
  result = yj.get_full_huali(solar, user_bazi)
"""

from dataclasses import dataclass, field
from datetime import datetime
from lunar_python import Solar

from .data.ganzhi import TIAN_GAN, DI_ZHI, ZHI_CHONG, GAN_HE


@dataclass
class FullHuangli:
    """完整黄历数据"""

    # === 日期基本信息 ===
    date: str                    # 公历日期 "2026-06-01"
    lunar_date: str              # 农历日期 "二〇二六年四月十六"
    day_ganzhi: str              # 日干支 "丙午"
    day_gan: str
    day_zhi: str
    shengxiao: str               # 生肖 "马"
    xiu: str                     # 二十八星宿 "心"
    xiu_luck: str                # 星宿吉凶 "凶"
    jianchu: str                 # 建除十二神 "除"
    week: str                    # 星期

    # === 冲煞 ===
    chong_shengxiao: str         # 冲生肖 "鼠"
    chong_desc: str              # 冲煞描述 "(庚子)鼠"
    sha_direction: str           # 煞方 "北"

    # === 值神 ===
    tianshen: str                # 值神 "青龙"
    tianshen_type: str           # 黄道/黑道
    tianshen_luck: str           # 吉/凶
    jishen: list                 # 吉神列表
    xiongsha: list               # 凶煞列表

    # === 每日宜忌（详细） ===
    yi: list                     # 宜事项
    ji: list                     # 忌事项

    # === 彭祖百忌 ===
    pengzu_gan: str              # 日干忌
    pengzu_zhi: str              # 日支忌

    # === 吉神方位 ===
    caishen: str                 # 财神方位
    xishen: str                  # 喜神方位
    fushen: str                  # 福神方位
    yanggui: str                 # 阳贵方位
    yingui: str                  # 阴贵方位

    # === 胎神 ===
    taishen: str                 # 胎神占方

    # === 九星 ===
    jiuxing: str                 # 当日九星

    # === 时辰吉凶（12时辰） ===
    hours: list = field(default_factory=list)

    # === 古籍参考 ===
    classical_ref: str = ""

    # === 个人维度（如有用户八字） ===
    personal: dict = field(default_factory=dict)


class DailyYiji:
    """老黄历完整引擎"""

    def get_full_huangli(self, solar: Solar, user_bazi=None) -> FullHuangli:
        """
        获取某日的完整黄历数据。

        Args:
            solar: lunar_python Solar 对象
            user_bazi: BaziResult 对象（可选）
        """
        lunar = solar.getLunar()

        # === 日期基本信息 ===
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()

        # === 时辰处理 ===
        # 十二时辰名称映射
        SHICHEN_NAMES = {
            "子": "子时", "丑": "丑时", "寅": "寅时", "卯": "卯时",
            "辰": "辰时", "巳": "巳时", "午": "午时", "未": "未时",
            "申": "申时", "酉": "酉时", "戌": "戌时", "亥": "亥时",
        }
        hours = []
        for t in lunar.getTimes():
            zhi = t.getZhi()
            hours.append({
                "name": SHICHEN_NAMES.get(zhi, zhi + "时"),
                "zhi": zhi,
                "ganzhi": t.getGanZhi(),
                "time_range": f"{t.getMinHm()}-{t.getMaxHm()}",
                "yi": t.getYi(),
                "ji": t.getJi(),
                "tianshen": t.getTianShen(),
                "tianshen_type": t.getTianShenType(),
                "tianshen_luck": t.getTianShenLuck(),
                "caishen": t.getPositionCaiDesc(),
                "xishen": t.getPositionXiDesc(),
                "fushen": t.getPositionFuDesc(),
            })

        # === 古籍参考 ===
        classical_ref = (
            "《协纪辨方书》·本原·建除十二神考\n"
            "《协纪辨方书》·义例·黄道黑道\n"
            "《协纪辨方书》·卷三十二·嫁娶\n"
            "《协纪辨方书》·卷三十三·出行/移徙/修造宜忌"
        )

        result = FullHuangli(
            # 日期
            date=solar.toFullString(),
            lunar_date=f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}日",
            day_ganzhi=lunar.getDayInGanZhi(),
            day_gan=day_gan,
            day_zhi=day_zhi,
            shengxiao=lunar.getYearShengXiao(),
            xiu=lunar.getXiu(),
            xiu_luck=lunar.getXiuLuck(),
            jianchu=lunar.getZhiXing(),
            week=f"星期{lunar.getWeekInChinese()}",

            # 冲煞
            chong_shengxiao=lunar.getDayChongShengXiao(),
            chong_desc=lunar.getDayChongDesc(),
            sha_direction=lunar.getDaySha(),

            # 值神+吉凶煞
            tianshen=lunar.getDayTianShen(),
            tianshen_type=lunar.getDayTianShenType(),
            tianshen_luck=lunar.getDayTianShenLuck(),
            jishen=lunar.getDayJiShen(),
            xiongsha=lunar.getDayXiongSha(),

            # 宜忌
            yi=lunar.getDayYi(),
            ji=lunar.getDayJi(),

            # 彭祖
            pengzu_gan=lunar.getPengZuGan(),
            pengzu_zhi=lunar.getPengZuZhi(),

            # 吉神方位
            caishen=lunar.getDayPositionCaiDesc(),
            xishen=lunar.getDayPositionXiDesc(),
            fushen=lunar.getDayPositionFuDesc(),
            yanggui=lunar.getDayPositionYangGuiDesc(),
            yingui=lunar.getDayPositionYinGuiDesc(),

            # 胎神
            taishen=lunar.getDayPositionTai(),

            # 九星
            jiuxing=lunar.getDayNineStar(),

            # 时辰
            hours=hours,

            # 古籍
            classical_ref=classical_ref,
        )

        # 个人分析
        if user_bazi is not None:
            result.personal = self._analyze_personal(result, user_bazi)

        return result

    def _analyze_personal(self, hl: FullHuangli, user_bazi) -> dict:
        """基于用户八字的个人宜忌分析"""
        from .data.ganzhi import get_shishen, GAN_WUXING, ZHI_WUXING

        rizhu = user_bazi.rizhu
        rizhu_wx = user_bazi.rizhu_wuxing
        user_day_zhi = user_bazi.day.zhi
        day_gan = hl.day_gan
        day_zhi = hl.day_zhi

        personal = {"yi": [], "ji": [], "analysis": [], "score": 0}

        # 1. 日干十神分析
        shishen = get_shishen(rizhu, day_gan)
        shishen_map = {
            "正印": ("宜学习读书", "印星当令，利于学习和吸收知识"),
            "偏印": ("宜研究钻研", "偏印主智慧，适合深入研究"),
            "正官": ("宜处理公务", "官星当值，适合正式的社交和工作"),
            "七杀": ("宜谨言慎行", "七杀临日，凡事多加小心"),
            "正财": ("宜理财规划", "财星当旺，适合处理财务"),
            "偏财": ("宜投资考察", "偏财透出，适合考察商机"),
            "食神": ("宜享受美食", "食神主享乐，适合放松和美食"),
            "伤官": ("宜创作表达", "伤官主才华，适合创作和表达"),
            "比肩": ("宜独立行事", "比肩帮身，适合独当一面"),
            "劫财": ("宜谨慎开销", "劫财主竞争，注意财务和人际"),
        }
        if shishen in shishen_map:
            yi_item, analysis = shishen_map[shishen]
            personal["yi"].append(yi_item)
            personal["analysis"].append(f"今日{day_gan}{shishen}日，{analysis}。")
            personal["score"] += 1

        # 2. 地支冲合
        if ZHI_CHONG.get(day_zhi) == user_day_zhi:
            personal["ji"].append("远行")
            personal["ji"].append("重大决策")
            personal["analysis"].append(
                f"今日{day_zhi}与你日支{user_day_zhi}相冲，《协纪辨方书》认为日支逢冲宜静不宜动。"
            )
            personal["score"] -= 2

        # 检查六合
        from .data.ganzhi import ZHI_HE
        if ZHI_HE.get((day_zhi, user_day_zhi)):
            personal["yi"].append("社交会友")
            personal["yi"].append("合作洽谈")
            personal["analysis"].append(
                f"今日{day_zhi}与你日支{user_day_zhi}相合，传统上利于合作与社交。"
            )
            personal["score"] += 2

        # 3. 五行补缺分析
        scores = user_bazi.wuxing_scores
        weak_wx = min(scores, key=scores.get)
        strong_wx = max(scores, key=scores.get)
        day_gan_wx = GAN_WUXING.get(day_gan, "")
        day_zhi_wx = ZHI_WUXING.get(day_zhi, "")

        if day_gan_wx == weak_wx or day_zhi_wx == weak_wx:
            personal["yi"].append("学习进修")
            personal["yi"].append("保健养生")
            personal["analysis"].append(
                f"今日五行{day_gan_wx}旺，恰好补益你偏弱的{weak_wx}，"
                f"传统命理认为今日对你有扶助之力。"
            )
            personal["score"] += 1

        if day_gan_wx == strong_wx:
            personal["analysis"].append(
                f"今日{day_gan_wx}气与你过旺的五行相同，传统上宜静养，忌冲动。"
            )
            personal["score"] -= 1

        # 4. 冲生肖检查
        chong_sx = hl.chong_shengxiao
        # 需要通过年柱支获取用户生肖
        user_sx = _zhi_to_shengxiao(user_bazi.year.zhi)
        if chong_sx == user_sx:
            personal["ji"].append("重要决策")
            personal["ji"].append("冒险活动")
            personal["analysis"].append(
                f"今日本日冲{chong_sx}，与你生肖相同，传统上称为'日冲本命'，凡事多加谨慎。"
            )
            personal["score"] -= 2

        # 5. 综合评估
        if personal["score"] >= 2:
            personal["summary"] = "今日对你较为有利，宜积极行事。"
        elif personal["score"] <= -2:
            personal["summary"] = "今日对你略有不利，宜静不宜动，保持平常心。"
        else:
            personal["summary"] = "今日平平，无大吉无大凶，一切照常即可。"

        return personal


def _zhi_to_shengxiao(zhi: str) -> str:
    """地支→生肖"""
    MAP = {"子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
           "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
           "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪"}
    return MAP.get(zhi, "")


def get_today_full_huangli(user_bazi=None) -> FullHuangli:
    """获取今日完整黄历"""
    now = datetime.now()
    solar = Solar.fromYmdHms(now.year, now.month, now.day, 12, 0, 0)
    yj = DailyYiji()
    return yj.get_full_huangli(solar, user_bazi)
