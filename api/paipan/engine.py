"""
排盘核心引擎
============
基于 lunar-python 的四柱八字排盘。
所有计算均为确定性算法，不涉及AI。
"""

from dataclasses import dataclass, field
from typing import Optional
from lunar_python import Solar, Lunar

from .data.ganzhi import (
    TIAN_GAN, DI_ZHI,
    GAN_WUXING, ZHI_WUXING, ZHI_CANGGAN, ZHI_MAIN_QI,
    get_nayin, get_shishen, get_changsheng_stage,
    is_yang, GAN_HE, ZHI_HE, ZHI_CHONG, ZHI_XING, ZHI_HAI,
)


@dataclass
class Pillar:
    """一柱（年/月/日/时）"""
    position: str      # "年"/"月"/"日"/"时"
    gan: str           # 天干
    zhi: str           # 地支
    nayin: str         # 纳音
    gan_wuxing: str    # 天干五行
    zhi_wuxing: str    # 地支五行
    canggan: list      # 藏干列表 [{"gan": "甲", "score": 6}, ...]
    main_qi: str       # 主气天干
    shishen: str       # 十神（相对日主）
    changsheng: str    # 十二长生状态


@dataclass
class BaziResult:
    """完整八字排盘结果"""
    # 基本信息
    solar_date: str           # 公历日期
    lunar_date: str           # 农历日期
    shengxiao: str            # 生肖
    gender: str               # 性别

    # 四柱
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    # 日主
    rizhu: str                # 日干
    rizhu_wuxing: str         # 日主五行

    # 五行统计
    wuxing_scores: dict       # {"金": 20, "木": 30, ...}

    # 十神统计
    shishen_count: dict       # {"正官": 1, "七杀": 0, ...}

    # 大运（需要额外调用）
    dayun: list = field(default_factory=list)

    # 神煞（需要额外调用）
    shensha: dict = field(default_factory=dict)

    # 地支关系
    zhi_relations: dict = field(default_factory=dict)

    # 天干合
    gan_he_pairs: list = field(default_factory=list)


def paipan(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    gender: str = "男",
    tz: int = 8,
) -> BaziResult:
    """
    排盘主函数。

    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 小时 (0-23)
        minute: 分钟 (0-59)
        gender: "男" 或 "女"
        tz: 时区偏移，默认东八区

    Returns:
        BaziResult: 完整的八字排盘结果
    """
    # 1. 使用 lunar-python 计算
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    ba = lunar.getEightChar()

    # 2. 提取四柱干支
    gans = {
        "年": ba.getYearGan(),
        "月": ba.getMonthGan(),
        "日": ba.getDayGan(),
        "时": ba.getTimeGan(),
    }
    zhis = {
        "年": ba.getYearZhi(),
        "月": ba.getMonthZhi(),
        "日": ba.getDayZhi(),
        "时": ba.getTimeZhi(),
    }

    rizhu = gans["日"]  # 日主

    # 3. 构建四柱
    pillars = {}
    for pos in ["年", "月", "日", "时"]:
        gan = gans[pos]
        zhi = zhis[pos]
        pillars[pos] = Pillar(
            position=pos,
            gan=gan,
            zhi=zhi,
            nayin=get_nayin(gan, zhi),
            gan_wuxing=GAN_WUXING[gan],
            zhi_wuxing=ZHI_WUXING[zhi],
            canggan=[{"gan": cg, "score": sc} for cg, sc in ZHI_CANGGAN[zhi]],
            main_qi=ZHI_MAIN_QI[zhi],
            shishen=get_shishen(rizhu, gan),
            changsheng=get_changsheng_stage(rizhu, zhi),
        )

    # 4. 五行分数统计
    wuxing_scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    # 天干分数
    for pos in ["年", "月", "日", "时"]:
        wuxing_scores[GAN_WUXING[gans[pos]]] += 5
    # 地支藏干分数（月支加倍）
    for pos in ["年", "月", "日", "时"]:
        weight = 2 if pos == "月" else 1  # 月支权重加倍
        for cg, score in ZHI_CANGGAN[zhis[pos]]:
            wuxing_scores[GAN_WUXING[cg]] += score * weight

    # 5. 十神统计
    shishen_count = {}
    for pos in ["年", "月", "时"]:  # 日柱不算自己
        shishen_name = get_shishen(rizhu, gans[pos])
        shishen_count[shishen_name] = shishen_count.get(shishen_name, 0) + 1
    # 地支主气十神
    for pos in ["年", "月", "日", "时"]:
        shishen_name = get_shishen(rizhu, ZHI_MAIN_QI[zhis[pos]])
        shishen_count[shishen_name] = shishen_count.get(shishen_name, 0) + 0.5

    # 6. 地支关系
    zhi_list = [zhis[p] for p in ["年", "月", "日", "时"]]
    zhi_relations = _calc_zhi_relations(zhi_list)

    # 7. 天干合
    gan_list = [gans[p] for p in ["年", "月", "日", "时"]]
    gan_he_pairs = _calc_gan_he(gan_list)

    # 8. 组装结果
    # 生肖（年支推算）
    shengxiao_map = {"子":"鼠","丑":"牛","寅":"虎","卯":"兔","辰":"龙","巳":"蛇",
                     "午":"马","未":"羊","申":"猴","酉":"鸡","戌":"狗","亥":"猪"}
    shengxiao = shengxiao_map.get(zhis["年"], "")

    result = BaziResult(
        solar_date=solar.toFullString(),
        lunar_date=f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}日",
        shengxiao=shengxiao,
        gender=gender,
        year=pillars["年"],
        month=pillars["月"],
        day=pillars["日"],
        hour=pillars["时"],
        rizhu=rizhu,
        rizhu_wuxing=GAN_WUXING[rizhu],
        wuxing_scores=wuxing_scores,
        shishen_count=shishen_count,
        zhi_relations=zhi_relations,
        gan_he_pairs=gan_he_pairs,
    )

    return result


def _calc_zhi_relations(zhi_list: list) -> dict:
    """计算地支间的关系（六合/六冲/三刑/六害）"""
    relations = {"六合": [], "六冲": [], "三刑": [], "六害": []}
    positions = ["年", "月", "日", "时"]

    for i in range(4):
        for j in range(i + 1, 4):
            zi, zj = zhi_list[i], zhi_list[j]
            pair = f"{positions[i]}{positions[j]}"

            # 六合
            if ZHI_HE.get((zi, zj)):
                relations["六合"].append(f"{pair}({zi}{zj}合{ZHI_HE[(zi,zj)]})")

            # 六冲
            if ZHI_CHONG.get(zi) == zj:
                relations["六冲"].append(f"{pair}({zi}{zj}冲)")

            # 三刑
            if ZHI_XING.get(zi) == zj:
                relations["三刑"].append(f"{pair}({zi}{zj}刑)")

            # 六害
            if ZHI_HAI.get(zi) == zj:
                relations["六害"].append(f"{pair}({zi}{zj}害)")

    return relations


def _calc_gan_he(gan_list: list) -> list:
    """计算天干合"""
    pairs = []
    positions = ["年", "月", "日", "时"]
    for i in range(4):
        for j in range(i + 1, 4):
            gi, gj = gan_list[i], gan_list[j]
            he_result = GAN_HE.get((gi, gj))
            if he_result:
                pairs.append(f"{positions[i]}{positions[j]}({gi}{gj}合化{he_result})")
    return pairs


def to_dict(result: BaziResult) -> dict:
    """将排盘结果转为JSON友好的字典"""
    return {
        "solar_date": result.solar_date,
        "lunar_date": result.lunar_date,
        "shengxiao": result.shengxiao,
        "gender": result.gender,
        "rizhu": result.rizhu,
        "rizhu_wuxing": result.rizhu_wuxing,
        "pillars": {
            "year": {
                "gan": result.year.gan,
                "zhi": result.year.zhi,
                "ganzhi": result.year.gan + result.year.zhi,
                "nayin": result.year.nayin,
                "gan_wuxing": result.year.gan_wuxing,
                "zhi_wuxing": result.year.zhi_wuxing,
                "canggan": result.year.canggan,
                "main_qi": result.year.main_qi,
                "shishen": result.year.shishen,
                "changsheng": result.year.changsheng,
            },
            "month": {
                "gan": result.month.gan,
                "zhi": result.month.zhi,
                "ganzhi": result.month.gan + result.month.zhi,
                "nayin": result.month.nayin,
                "gan_wuxing": result.month.gan_wuxing,
                "zhi_wuxing": result.month.zhi_wuxing,
                "canggan": result.month.canggan,
                "main_qi": result.month.main_qi,
                "shishen": result.month.shishen,
                "changsheng": result.month.changsheng,
            },
            "day": {
                "gan": result.day.gan,
                "zhi": result.day.zhi,
                "ganzhi": result.day.gan + result.day.zhi,
                "nayin": result.day.nayin,
                "gan_wuxing": result.day.gan_wuxing,
                "zhi_wuxing": result.day.zhi_wuxing,
                "canggan": result.day.canggan,
                "main_qi": result.day.main_qi,
                "shishen": "日主",
                "changsheng": result.day.changsheng,
            },
            "hour": {
                "gan": result.hour.gan,
                "zhi": result.hour.zhi,
                "ganzhi": result.hour.gan + result.hour.zhi,
                "nayin": result.hour.nayin,
                "gan_wuxing": result.hour.gan_wuxing,
                "zhi_wuxing": result.hour.zhi_wuxing,
                "canggan": result.hour.canggan,
                "main_qi": result.hour.main_qi,
                "shishen": result.hour.shishen,
                "changsheng": result.hour.changsheng,
            },
        },
        "wuxing_scores": result.wuxing_scores,
        "shishen_count": result.shishen_count,
        "zhi_relations": result.zhi_relations,
        "gan_he_pairs": result.gan_he_pairs,
        "dayun": result.dayun,
        "shensha": result.shensha,
    }
