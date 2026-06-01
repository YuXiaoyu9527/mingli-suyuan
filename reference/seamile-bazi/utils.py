"""通用工具函数模块。"""

from __future__ import annotations

from .data.datas import KONG_WANG
from .data.ganzhi import (
    CANG_GAN,
    CANG_GAN_LIST,
    DI_ZHI,
    GAN_5,
    GONG_HE,
    SHI_SHEN,
    TIAN_GAN,
    XIANG_HE_GAN,
    ZHI_ATTR,
)


def yinyang(item: str) -> str:
    """判断天干/地支的阴阳。"""
    if item in TIAN_GAN:
        return '＋' if TIAN_GAN.index(item) % 2 == 0 else '－'
    return '＋' if DI_ZHI.index(item) % 2 == 0 else '－'


def is_yang_gan(gan: str) -> bool:
    """判断天干是否为阳干。"""
    return TIAN_GAN.index(gan) % 2 == 0


def check_gan(gan: str, gans: tuple | list) -> str:
    """检查天干的合冲关系。"""
    result = ''
    if SHI_SHEN[gan]['合'] in gans:
        result += '合' + SHI_SHEN[gan]['合']
    if SHI_SHEN[gan]['冲'] in gans:
        result += '冲' + SHI_SHEN[gan]['冲']
    return result


def get_empty(day_zhu: tuple, zhi: str) -> str:
    """检查空亡。"""
    empty = KONG_WANG[day_zhu]
    if zhi in empty:
        return '空'
    return ''


def is_kong_wang(day_zhu: tuple, zhi: str) -> bool:
    """检查是否空亡（返回 bool）。"""
    return zhi in KONG_WANG[day_zhu]


def get_gen(gan: str, zhis: tuple | list) -> dict:  # noqa: C901
    """计算天干在地支中的根。

    返回 {"强": [...], "中": [...], "弱": [...], "text": "..."} 或 {"无根": True}
    """
    zhus = []
    zhongs = []
    weis = []

    for item in zhis:
        zhu = CANG_GAN_LIST[item][0]
        if SHI_SHEN[gan]['本'] == SHI_SHEN[zhu]['本']:
            zhus.append(item)

    for item in zhis:
        if len(CANG_GAN_LIST[item]) == 1:
            continue
        zhong = CANG_GAN_LIST[item][1]
        if SHI_SHEN[gan]['本'] == SHI_SHEN[zhong]['本']:
            zhongs.append(item)

    for item in zhis:
        if len(CANG_GAN_LIST[item]) < 3:
            continue
        wei = CANG_GAN_LIST[item][2]
        if SHI_SHEN[gan]['本'] == SHI_SHEN[wei]['本']:
            weis.append(item)

    if not (zhus or zhongs or weis):
        return {'无根': True, 'text': '无根'}

    parts = []
    if zhus:
        parts.append(f'强：{"".join(zhus)}')
    if zhongs:
        parts.append(f'中：{"".join(zhongs)}')
    if weis:
        parts.append(f'弱：{"".join(weis)}')
    return {
        '强': zhus,
        '中': zhongs,
        '弱': weis,
        '无根': False,
        'text': '　'.join(parts),
    }


def gan_zhi_he(gan: str, zhi: str) -> bool:
    """检查天干地支是否暗合（天干的合在地支藏干中）。"""
    return SHI_SHEN[gan]['合'] in CANG_GAN[zhi]


def get_gong(gans: tuple | list, zhis: tuple | list) -> list:
    """计算地支拱合。"""
    result = []
    for i in range(3):
        if gans[i] != gans[i + 1]:
            continue
        zhi1 = zhis[i]
        zhi2 = zhis[i + 1]
        if abs(DI_ZHI.index(zhi1) - DI_ZHI.index(zhi2)) == 2:
            value = DI_ZHI[(DI_ZHI.index(zhi1) + DI_ZHI.index(zhi2)) // 2]
            result.append(value)
        if (zhi1 + zhi2 in GONG_HE) and (GONG_HE[zhi1 + zhi2] not in zhis):
            result.append(GONG_HE[zhi1 + zhi2])
    return result


def check_gong(
    zhis: tuple | list,
    n1: int,
    n2: int,
    me: str,
    hes: dict,
    desc: str = '三合拱',
) -> str:
    """检查三合/三会的拱合。"""
    result = ''
    key = zhis[n1] + zhis[n2]
    if key in hes:
        gong = hes[key]
        if gong not in zhis:
            detail = get_zhi_detail(gong, me)
            result += f'\t{desc}：{zhis[n1]}{zhis[n2]}-{gong}[{detail}]'
    return result


def get_zhi_detail(zhi: str, me: str, multi: int = 1) -> str:
    """获取地支藏干详细信息。"""
    out = ''
    for gan in CANG_GAN[zhi]:
        out += f'{gan}{GAN_5[gan]}{CANG_GAN[zhi][gan] * multi}{SHI_SHEN[me][gan]} '
    return out.rstrip()


def is_ku(zhi: str) -> bool:
    """判断地支是否为库。"""
    return zhi in '辰戌丑未'


def zhi_ku(zhi: str, items: tuple) -> bool:
    """判断地支是否为某些天干的库。"""
    return is_ku(zhi) and min(CANG_GAN[zhi], key=CANG_GAN[zhi].get) in items


def gan_ke(gan1: str, gan2: str) -> bool:
    """判断两个天干是否存在相克关系。"""
    return SHI_SHEN[gan1]['克'] == SHI_SHEN[gan2]['本'] or SHI_SHEN[gan2]['克'] == SHI_SHEN[gan1]['本']


def jin_jiao(first: str, second: str) -> bool:
    """判断是否进角。"""
    return DI_ZHI.index(second) - DI_ZHI.index(first) == 1


def calc_direction(year_gan: str, is_female: bool) -> int:
    """计算大运方向。

    返回 1 (顺行) 或 -1 (逆行)。
    """
    seq = TIAN_GAN.index(year_gan)
    if is_female:
        return -1 if seq % 2 == 0 else 1
    return 1 if seq % 2 == 0 else -1


def calc_dayun_ganzhi(
    month_gan: str,
    month_zhi: str,
    direction: int,
    count: int = 12,
) -> list[str]:
    """计算大运干支序列。"""
    dayuns = []
    gan_seq = TIAN_GAN.index(month_gan)
    zhi_seq = DI_ZHI.index(month_zhi)
    for _ in range(count):
        gan_seq += direction
        zhi_seq += direction
        dayuns.append(TIAN_GAN[gan_seq % 10] + DI_ZHI[zhi_seq % 12])
    return dayuns


def calc_gan_he_list(gans: tuple | list) -> list[bool]:
    """计算天干合（相邻才算）。"""
    result = [False, False, False, False]
    for i in range(3):
        if (gans[i], gans[i + 1]) in set(XIANG_HE_GAN) or (gans[i + 1], gans[i]) in set(XIANG_HE_GAN):
            result[i] = result[i + 1] = True
    return result


def calc_zhi_6he(zhis: tuple | list) -> list[bool]:
    """计算地支六合（相邻才算）。"""
    result = [False, False, False, False]
    for i in range(3):
        if ZHI_ATTR[zhis[i]]['六'] == zhis[i + 1]:
            result[i] = result[i + 1] = True
    return result


def calc_zhi_6chong(zhis: tuple | list) -> list[bool]:
    """计算地支六冲（相邻才算）。"""
    result = [False, False, False, False]
    for i in range(3):
        if ZHI_ATTR[zhis[i]]['冲'] == zhis[i + 1]:
            result[i] = result[i + 1] = True
    return result


def calc_zhi_xing(zhis: tuple | list) -> list[bool]:
    """计算地支刑（相邻才算）。"""
    result = [False, False, False, False]
    for i in range(3):
        if ZHI_ATTR[zhis[i]]['刑'] == zhis[i + 1] or ZHI_ATTR[zhis[i + 1]]['刑'] == zhis[i]:
            result[i] = result[i + 1] = True
    return result
