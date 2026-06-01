"""
神煞计算模块
============
基于确定性的查找表算法，不涉及AI。
所有规则来自《三命通会》和《协纪辨方书》。
"""

from .data.ganzhi import TIAN_GAN, DI_ZHI, ZHI_CHONG, ZHI_HE, ZHI_SANHE


def calc_shensha(
    year_zhi: str,
    month_zhi: str,
    day_gan: str,
    day_zhi: str,
    hour_zhi: str,
    month_gan: str,
) -> dict:
    """
    计算常用神煞。

    Args:
        year_zhi: 年支
        month_zhi: 月支
        day_gan: 日干
        day_zhi: 日支
        hour_zhi: 时支
        month_gan: 月干

    Returns:
        {神煞名: [位置, ...]}
    """
    all_zhi = {
        "年": year_zhi,
        "月": month_zhi,
        "日": day_zhi,
        "时": hour_zhi,
    }

    shensha = {}

    # 天乙贵人（日干/年干查）
    tianyi = _calc_tianyi(day_gan)
    for pos, zhi in all_zhi.items():
        if zhi in tianyi:
            shensha.setdefault("天乙贵人", []).append(pos)

    # 文昌贵人（日干查）
    wenchang = _calc_wenchang(day_gan)
    for pos, zhi in all_zhi.items():
        if zhi in wenchang:
            shensha.setdefault("文昌贵人", []).append(pos)

    # 驿马（年支或日支查）
    yima = _calc_yima(year_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in yima:
            shensha.setdefault("驿马", []).append(pos)

    # 桃花/咸池（年支或日支查）
    taohua = _calc_taohua(year_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in taohua:
            shensha.setdefault("桃花", []).append(pos)

    # 华盖（年支或日支查）
    huagai = _calc_huagai(year_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in huagai:
            shensha.setdefault("华盖", []).append(pos)

    # 羊刃（日干查）
    yangren = _calc_yangren(day_gan)
    for pos, zhi in all_zhi.items():
        if zhi in yangren:
            shensha.setdefault("羊刃", []).append(pos)

    # 空亡（日柱查）
    kongwang = _calc_kongwang(day_gan, day_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in kongwang:
            shensha.setdefault("空亡", []).append(pos)

    # 将星（年支或日支查）
    jiangxing = _calc_jiangxing(year_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in jiangxing:
            shensha.setdefault("将星", []).append(pos)

    # 月德贵人（月支查）
    yuede_zhi = _calc_yuede(month_zhi)
    for pos, zhi in all_zhi.items():
        if zhi in yuede_zhi:
            shensha.setdefault("月德贵人", []).append(pos)

    return shensha


def _calc_tianyi(gan: str) -> list[str]:
    """天乙贵人：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛逢虎马"""
    MAP = {
        "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
        "乙": ["子", "申"], "己": ["子", "申"],
        "丙": ["亥", "酉"], "丁": ["亥", "酉"],
        "壬": ["卯", "巳"], "癸": ["卯", "巳"],
        "辛": ["午", "寅"],
    }
    return MAP.get(gan, [])


def _calc_wenchang(gan: str) -> list[str]:
    """文昌贵人：甲巳乙午报君知，丙戊申宫丁己鸡，庚猪辛鼠壬逢虎，癸人见兔入云梯"""
    MAP = {
        "甲": ["巳"], "乙": ["午"],
        "丙": ["申"], "丁": ["酉"],
        "戊": ["申"], "己": ["酉"],
        "庚": ["亥"], "辛": ["子"],
        "壬": ["寅"], "癸": ["卯"],
    }
    return MAP.get(gan, [])


def _calc_yima(zhi: str) -> list[str]:
    """驿马：申子辰马在寅，寅午戌马在申，巳酉丑马在亥，亥卯未马在巳"""
    for trio, ma in [(["申", "子", "辰"], "寅"), (["寅", "午", "戌"], "申"),
                      (["巳", "酉", "丑"], "亥"), (["亥", "卯", "未"], "巳")]:
        if zhi in trio:
            return [ma]
    return []


def _calc_taohua(zhi: str) -> list[str]:
    """桃花/咸池：申子辰在酉，寅午戌在卯，巳酉丑在午，亥卯未在子"""
    for trio, hua in [(["申", "子", "辰"], "酉"), (["寅", "午", "戌"], "卯"),
                       (["巳", "酉", "丑"], "午"), (["亥", "卯", "未"], "子")]:
        if zhi in trio:
            return [hua]
    return []


def _calc_huagai(zhi: str) -> list[str]:
    """华盖：申子辰在辰，寅午戌在戌，巳酉丑在丑，亥卯未在未"""
    for trio, gai in [(["申", "子", "辰"], "辰"), (["寅", "午", "戌"], "戌"),
                       (["巳", "酉", "丑"], "丑"), (["亥", "卯", "未"], "未")]:
        if zhi in trio:
            return [gai]
    return []


def _calc_yangren(gan: str) -> list[str]:
    """羊刃（阳干帝旺位）：甲刃在卯，丙戊刃在午，庚刃在酉，壬刃在子"""
    MAP = {"甲": ["卯"], "丙": ["午"], "戊": ["午"], "庚": ["酉"], "壬": ["子"]}
    return MAP.get(gan, [])


def _calc_kongwang(day_gan: str, day_zhi: str) -> list[str]:
    """空亡：以日柱干支查旬空"""
    # 六十甲子分六旬，每旬空两个地支
    ganzhi = day_gan + day_zhi
    # 六甲旬
    xun_tou = {
        "甲子": ["戌", "亥"], "甲戌": ["申", "酉"],
        "甲申": ["午", "未"], "甲午": ["辰", "巳"],
        "甲辰": ["寅", "卯"], "甲寅": ["子", "丑"],
    }
    # 找所属旬
    gan_idx = TIAN_GAN.index(day_gan)
    zhi_idx = DI_ZHI.index(day_zhi)
    # 天干从甲开始到当前干的位置，地支对应偏移
    offset = gan_idx
    xun_tou_zhi = DI_ZHI[(zhi_idx - offset) % 12]
    xun_tou_gan = "甲"
    xun_key = xun_tou_gan + xun_tou_zhi
    return xun_tou.get(xun_key, [])


def _calc_jiangxing(zhi: str) -> list[str]:
    """将星：申子辰在子，巳酉丑在酉，寅午戌在午，亥卯未在卯"""
    for trio, jiang in [(["申", "子", "辰"], "子"), (["巳", "酉", "丑"], "酉"),
                         (["寅", "午", "戌"], "午"), (["亥", "卯", "未"], "卯")]:
        if zhi in trio:
            return [jiang]
    return []


def _calc_yuede(month_zhi: str) -> list[str]:
    """月德贵人：寅午戌月见丙，申子辰月见壬，亥卯未月见甲，巳酉丑月见庚"""
    # 月德查的是天干在四柱中出现的位置
    MAP = {
        "寅": "丙", "午": "丙", "戌": "丙",
        "申": "壬", "子": "壬", "辰": "壬",
        "亥": "甲", "卯": "甲", "未": "甲",
        "巳": "庚", "酉": "庚", "丑": "庚",
    }
    return [MAP.get(month_zhi, "")]
