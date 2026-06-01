"""命理分析引擎 - 十神分析、格局判断、特殊星宿等。"""

from __future__ import annotations

from .data.datas import (
    GE_JU,
    JIAN_LU,
    JIAN_LU_DESC,
    JIN_BU_HUAN,
    JIN_BU_HUAN_DESC,
    LU,
    NA_YIN,
    RI_ZHU,
    TIAN_YI,
    TIAN_YIN,
    TIAO_HOU,
    WEN_XING,
    YU_TANG,
    self_zuo,
)
from .data.ganzhi import (
    CANG_GAN,
    DI_ZHI,
    GAN_3,
    GAN_4,
    GAN_DESC,
    GONG_HE,
    SAN_HE_JU,
    SAN_HUI_GONG,
    SHI_SHEN,
    TIAN_GAN,
    WU_XING,
    ZHI_3,
    ZHI_DESC,
    ZHI_HES,
    ZHI_HUIS,
)
from .utils import (
    check_gong,
)


class Analyzer:
    """命理分析引擎。"""

    def __init__(self, calc):
        self.calc = calc
        self.me = calc.me
        self.gans = calc.gans
        self.zhis = calc.zhis
        self.zhus = calc.zhus
        self.gan_shens = calc.gan_shens
        self.zhi_shens = calc.zhi_shens
        self.zhi_shens2 = calc.zhi_shens2
        self.zhi_shen3 = calc.zhi_shen3
        self.shens = calc.shens
        self.shens2 = calc.shens2
        self.shen_zhus = calc.shen_zhus
        self.statuses = calc.statuses
        self.scores = calc.scores
        self.is_female = calc.is_female

    def get_geju(self) -> dict:
        """格局分析。"""
        ge = self._determine_ge()
        tiaohou = self._get_tiaohou()
        jin = self._get_jinbuhuan()
        ge_list = self._get_ge_list()
        jus = self._get_ju()
        all_ges = self._collect_all_ges()

        return {
            '格': ge,
            '局': jus,
            '成格': all_ges,
            '调候': tiaohou,
            '金不换': jin,
            '格局选用': ge_list,
        }

    def _determine_ge(self) -> str:
        me = self.me
        zhis = self.zhis
        gans = self.gans

        if (me, zhis[1]) in JIAN_LU:
            return '建'
        if (me, zhis[1]) in (('甲', '卯'), ('庚', '酉'), ('壬', '子')):
            return '月刃'

        zhi = zhis[1]
        if zhi in WU_XING['土'] or (me, zhis[1]) in (
            ('乙', '寅'),
            ('丙', '午'),
            ('丁', '巳'),
            ('戊', '午'),
            ('己', '巳'),
            ('辛', '申'),
            ('癸', '亥'),
        ):
            for item in CANG_GAN[zhi]:
                if item in gans[:2] + gans[3:]:
                    return SHI_SHEN[me][item]
        else:
            d = CANG_GAN[zhi]
            return SHI_SHEN[me][max(d, key=d.get)]
        return ''

    def _get_tiaohou(self) -> str:
        key = self.me + self.zhis[1]
        return TIAO_HOU.get(key, '')

    def _get_jinbuhuan(self) -> list[str]:
        result = []
        key = self.me + self.zhis[1]
        if key in JIN_BU_HUAN:
            result.append(JIN_BU_HUAN[key])
        for jin_key, jin_val in JIN_BU_HUAN_DESC.items():
            if jin_key == self.me + self.zhis[1]:
                result.append(jin_val)
        return result

    def _get_ge_list(self) -> list[str]:
        result = []
        key = self.me + self.zhis[1]
        if key in GE_JU:
            result.append(GE_JU[key])
        return result

    def _get_ju(self) -> list[str]:
        result = []
        zhis_set = set(self.zhis) | set(getattr(self.calc, 'gongs', []))

        # 检查三合局和三会局
        for items in (ZHI_HES, ZHI_HUIS):
            for combination, element in items.items():
                if set(combination).issubset(zhis_set):
                    # 利用 SHI_SHEN 的反查功能获取关系键（如 '本', '被克' 等）
                    rel_key = SHI_SHEN[self.me].inverse.get(element)
                    if rel_key in SAN_HE_JU:
                        result.append(SAN_HE_JU[rel_key])
        return result

    def _collect_all_ges(self) -> list[str]:
        gs = self.gan_shens
        zs2 = self.zhi_shens2

        return [
            shen for shen in ('印', '枭', '比', '劫', '才', '财', '官', '杀', '食', '伤') if shen in gs and shen in zs2
        ]

    def get_shishen_analysis(self) -> dict[str, list[str]]:
        """十神详细分析，返回按类别分组的文本列表。"""
        result = {}
        for method_name in (
            '_analyze_bi',
            '_analyze_jie',
            '_analyze_yin',
            '_analyze_xiao',
            '_analyze_piancai',
            '_analyze_zhengcai',
            '_analyze_guan',
            '_analyze_sha',
            '_analyze_shi',
            '_analyze_shang',
        ):
            method = getattr(self, method_name)
            items = method()
            if items:
                category = method_name.replace('_analyze_', '')
                result[category] = items
        return result

    def _analyze_bi(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '比' in gs:
            r.append('同性相斥。讨厌自己一样的人。比肩多又无官杀的人自尊心强。')
            if gs.count('比') > 1 or self.shens2.count('比') > 2:
                r.append('比肩多，有分夺之象。')
        if self.zhi_shens[2] == '比':
            r.append('自坐比肩：女命夫缘不佳。男命妻缘不佳。')
        return r

    def _analyze_jie(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '劫' in gs:
            r.append('劫财个性强烈、积极进取、争夺心强。')
            if '财' in gs or '才' in gs:
                r.append('劫财透干遇财，投资要谨慎。')
        return r

    def _analyze_yin(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '印' in gs:
            r.append('正印仁慈，心性慈悲。印多身旺不利。')
            if '印' in self.zhi_shens2:
                r.append('正印成格：喜官杀。')
        return r

    def _analyze_xiao(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '枭' in gs:
            r.append('偏印精明、机警。枭多则孤僻。')
            if '食' in gs:
                r.append('枭神夺食：不利。若有偏财可解。')
        return r

    def _analyze_piancai(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '才' in gs:
            r.append('偏财豪爽、大方。人缘好。')
            if '才' in self.zhi_shens2:
                r.append('偏财成格：喜身旺。')
        return r

    def _analyze_zhengcai(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '财' in gs:
            r.append('正财勤劳节俭，正当收入。')
            if '财' in self.zhi_shens2:
                r.append('正财成格：忌劫财、比肩。有官保护则无忧。')
        return r

    def _analyze_guan(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '官' in gs:
            r.append('正官守法、有信用、重名誉。')
            if '官' in self.zhi_shens2:
                r.append('官成格：忌伤；忌混杂。有伤用财通关或印制。')
            if '伤' in gs:
                r.append('正官伤官通根透，婚姻不美满概率大。')
            if gs[0] == '官':
                r.append('年干为官，身强可能出身书香门第。')
        return r

    def _analyze_sha(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '杀' in gs:
            r.append('七杀是非多，但对男人有时是贵格。成格喜食制、阳刃驾杀、身杀两停。')
            if '杀' in self.zhi_shens2:
                r.append('杀格：喜食神制，要食在前，杀在后。')
            if gs[0] == '杀':
                r.append('年干七杀，早年不好。或家里穷或身体不好。')
            if '印' in gs:
                r.append('身弱杀生印，不少是精明练达的商人。')
        return r

    def _analyze_shi(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '食' in gs:
            r.append('食神有口福，厚道。成格基础84，喜财忌偏印。')
            if '食' in self.zhi_shens2:
                r.append('食神成格：寿命比较好。食神和偏财格比较长寿。')
            if '枭' in gs:
                r.append('食神碰到偏印，身体不好。四柱透出偏财可解。')
        return r

    def _analyze_shang(self) -> list[str]:
        r = []
        gs = self.gan_shens
        if '伤' in gs:
            r.append('伤官有才华，但是清高。要生财，或者印制。')
            if '伤' in self.zhi_shens2:
                r.append('伤官成格：生财、配印。')
            if '印' in gs and '财' not in gs:
                r.append('伤官配印，无财，有手艺，但不善于理财。')
        return r

    def get_special_analysis(self) -> dict[str, list[str]]:  # noqa: C901
        """特殊格局和杂项分析。"""
        result = {}
        # 日柱分析
        day_gz = self.me + self.zhis[2]
        if day_gz in RI_ZHU:
            result['日柱'] = [RI_ZHU[day_gz]]

        # 天元坐支
        zuo = []
        for item in CANG_GAN[self.zhis[2]]:
            name = SHI_SHEN[self.me][item]
            text = self_zuo.get(name, '')
            if text.strip():
                zuo.append(text.strip())
        if zuo:
            result['天元坐支'] = zuo

        # 出身
        cai = SHI_SHEN[self.me].inverse['财']
        guan = SHI_SHEN[self.me].inverse['官']
        births = tuple(self.gans[:2])
        if cai in births and guan in births:
            result['出身'] = ['不错']
        else:
            result['出身'] = ['一般']

        # 天干描述
        result['日主特点'] = [GAN_DESC.get(self.me, '')]
        result['年支特点'] = [ZHI_DESC.get(self.zhis[0], '')]

        # 三字干/四字干/三字支
        gan_t = tuple(self.gans)
        for item in TIAN_GAN:
            if gan_t.count(item) == 3 and item in GAN_3:
                result['三字干'] = [f'{item}：{GAN_3[item]}']
                break
            if gan_t.count(item) == 4 and item in GAN_4:
                result['四字干'] = [f'{item}：{GAN_4[item]}']
                break

        zhi_t = tuple(self.zhis)
        for item in DI_ZHI:
            if zhi_t.count(item) > 2 and item in ZHI_3:
                result['三字支'] = [f'{item}：{ZHI_3[item]}']
                break

        return result

    def get_special_stars(self) -> dict[str, list[str]]:  # noqa: C901
        """特殊星宿：贵人、将星、华盖、桃花、禄等。"""
        result = {}
        me = self.me
        zhis = self.zhis

        # 天乙贵人
        ty = TIAN_YI.get(me, '')
        if ty and ty in zhis:
            result['天乙贵人'] = [ty]

        # 玉堂贵人
        yt = YU_TANG.get(me, '')
        if yt and yt in zhis:
            result['玉堂贵人'] = [yt]

        # 天罗
        if NA_YIN.get(self.zhus[0], '')[-1:] == '火':
            if zhis[2] in '戌亥':
                result['天罗'] = [zhis[2]]

        # 地网
        ny = NA_YIN.get(self.zhus[0], '')
        if ny and ny[-1] in '水土':
            if zhis[2] in '辰巳':
                result['地网'] = [zhis[2]]

        # 文星贵人
        wx = WEN_XING.get(me, '')
        if wx and wx in zhis:
            result['文星贵人'] = [wx]

        # 天印贵人
        tyi = TIAN_YIN.get(me, '')
        if tyi and tyi in zhis:
            result['天印贵人'] = [tyi]

        # 将星
        me_zhi = zhis[2]
        others = list(zhis[:2]) + list(zhis[3:])
        jiang_map = {
            ('申', '子', '辰'): '子',
            ('丑', '巳', '酉'): '酉',
            ('寅', '午', '戌'): '午',
            ('亥', '卯', '未'): '卯',
        }
        for group, target in jiang_map.items():
            if me_zhi in group and target in others:
                result['将星'] = [target]
                break

        # 华盖
        huagai_map = {
            ('申', '子', '辰'): '辰',
            ('丑', '巳', '酉'): '丑',
            ('寅', '午', '戌'): '戌',
            ('亥', '卯', '未'): '未',
        }
        for group, target in huagai_map.items():
            if me_zhi in group and target in others:
                result['华盖'] = [target]
                break

        # 桃花
        year_zhi = zhis[0]
        taohua_map = {
            ('申', '子', '辰'): '酉',
            ('丑', '巳', '酉'): '午',
            ('寅', '午', '戌'): '卯',
            ('亥', '卯', '未'): '子',
        }
        for group, target in taohua_map.items():
            if (me_zhi in group or year_zhi in group) and target in zhis:
                result['桃花'] = [target]
                break

        # 禄分析
        lu_items = []
        if me in LU:
            for zhu_tuple, desc in LU[me].items():
                if zhu_tuple in self.zhus:
                    lu_items.append(f'{"".join(zhu_tuple)}：{desc}')
        if lu_items:
            result['禄'] = lu_items

        # 羊刃
        key = '帝' if TIAN_GAN.index(me) % 2 == 0 else '冠'
        yr = SHI_SHEN[me].inverse[key]
        if yr in zhis:
            result['羊刃'] = [f'{me} {yr}']

        return result

    def get_jianlu(self) -> dict | None:
        """建禄格信息。"""
        me = self.me
        key = (me, self.zhis[1])
        if key in JIAN_LU:
            return {
                'desc': JIAN_LU_DESC,
                'detail': JIAN_LU[key],
            }
        return None

    def get_gong_analysis(self) -> list[str]:
        """拱合分析。"""
        result = []
        r = check_gong(self.zhis, 1, 2, self.me, GONG_HE)
        if r:
            result.append(r.strip())
        r = check_gong(self.zhis, 1, 2, self.me, SAN_HUI_GONG, '三会拱')
        if r:
            result.append(r.strip())
        return result
