"""
大运计算模块
============
基于年柱天干阴阳 + 性别确定顺逆排，
从月柱起运，按"阳男阴女顺排，阴男阳女逆排"规则。
"""

from .data.ganzhi import TIAN_GAN, DI_ZHI, is_yang, get_nayin


def calc_dayun(
    year_gan: str,
    month_gan: str,
    month_zhi: str,
    gender: str,
    birth_solar_term_day: int,
    next_solar_term_day: int,
    prev_solar_term_day: int,
) -> list[dict]:
    """
    计算大运。

    Args:
        year_gan: 年柱天干
        month_gan: 月柱天干
        month_zhi: 月柱地支
        gender: "男" 或 "女"
        birth_solar_term_day: 出生日距离上一个节气的天数
        next_solar_term_day: 出生日距离下一个节气的天数
        prev_solar_term_day: 出生日距离上一个节气的天数

    Returns:
        大运列表，每项含 干支/起运年龄/纳音/十干运
    """
    # 1. 判断顺逆
    year_yang = is_yang(year_gan)
    is_male = gender == "男"

    # 阳男阴女 → 顺排；阴男阳女 → 逆排
    forward = (year_yang and is_male) or (not year_yang and not is_male)

    # 2. 起运年龄
    if forward:
        # 顺排：从出生日到下一个节气的天数
        days_to_term = next_solar_term_day
    else:
        # 逆排：从上一个节气到出生日的天数
        days_to_term = prev_solar_term_day

    # 3天为1岁，1天=4个月
    qiyun_age = max(1, round(days_to_term / 3))

    # 3. 生成大运干支序列
    month_gan_idx = TIAN_GAN.index(month_gan)
    month_zhi_idx = DI_ZHI.index(month_zhi)

    dayun_list = []
    for i in range(1, 11):  # 排10步大运
        step = i if forward else -i
        gan_idx = (month_gan_idx + step) % 10
        zhi_idx = (month_zhi_idx + step) % 12

        gan = TIAN_GAN[gan_idx]
        zhi = DI_ZHI[zhi_idx]
        ganzhi = gan + zhi

        dayun_list.append({
            "step": i,
            "ganzhi": ganzhi,
            "gan": gan,
            "zhi": zhi,
            "nayin": get_nayin(gan, zhi),
            "start_age": qiyun_age + (i - 1) * 10,
            "end_age": qiyun_age + i * 10 - 1,
        })

    return dayun_list


def calc_dayun_from_lunar(lunar_obj, year_gan: str, month_gan: str, month_zhi: str, gender: str) -> list[dict]:
    """
    使用 lunar-python 的 Lunar 对象精确计算大运。

    使用 lunar-python 内置的节气计算来获取更精确的起运信息。
    """
    # 获取节气信息
    jieqi_table = lunar_obj.getJieQiTable()
    birth_solar = lunar_obj.getSolar()
    birth_julian = birth_solar.getJulianDay()

    # lunar-python 的节气表是 {节气名: Solar对象}
    # 我们需要找到出生前后的节气
    prev_jie = None
    next_jie = None

    jie_names = [
        "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
        "立秋", "白露", "寒露", "立冬", "大雪", "小寒",
    ]

    prev_days = 999
    next_days = 999

    for jie_name, jie_solar in jieqi_table.items():
        if jie_name not in jie_names:
            continue
        jie_julian = jie_solar.getJulianDay()
        diff = jie_julian - birth_julian

        if diff < 0 and abs(diff) < prev_days:
            prev_days = abs(diff)
            prev_jie = jie_name
        elif diff >= 0 and diff < next_days:
            next_days = diff
            next_jie = jie_name

    prev_solar_days = prev_days if prev_days != 999 else 3
    next_solar_days = next_days if next_days != 999 else 3

    return calc_dayun(
        year_gan=year_gan,
        month_gan=month_gan,
        month_zhi=month_zhi,
        gender=gender,
        birth_solar_term_day=0,
        next_solar_term_day=next_solar_days,
        prev_solar_term_day=prev_solar_days,
    )
