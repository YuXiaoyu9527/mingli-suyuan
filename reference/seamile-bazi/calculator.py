"""核心计算引擎 - 负责从输入信息计算出八字排盘的基础数据。"""

from __future__ import annotations

from collections import OrderedDict

from bidict import bidict
from lunar_python import Lunar, Solar

from .data.datas import NA_YIN, XIU_QIU
from .data.ganzhi import (
    CANG_GAN,
    GAN_5,
    NEI_ZANG_GAN,
    NEI_ZANG_ZHI,
    RELATION,
    SHI_SHEN,
    TEMPERATURE,
    TIAN_GAN,
    WU_XING_ZHI,
    ZHI_ATTR,
)
from .utils import (
    calc_dayun_ganzhi,
    calc_direction,
    calc_gan_he_list,
    calc_zhi_6chong,
    calc_zhi_6he,
    calc_zhi_xing,
    check_gan,
    gan_zhi_he,
    get_gen,
    get_gong,
    is_kong_wang,
    yinyang,
)


class FourPillars:
    """四柱数据容器。"""

    def __init__(
        self,
        gans: tuple[str, str, str, str],
        zhis: tuple[str, str, str, str],
    ):
        self.gans = gans
        self.zhis = zhis
        self.year_gan, self.month_gan, self.day_gan, self.time_gan = gans
        self.year_zhi, self.month_zhi, self.day_zhi, self.time_zhi = zhis
        self.me = self.day_gan
        self.zhus = list(zip(gans, zhis, strict=False))

    @property
    def four_ganzhi(self) -> list[str]:
        return [g + z for g, z in self.zhus]


class Calculator:
    """核心计算引擎。"""

    def __init__(
        self,
        pillars: FourPillars,
        is_female: bool,
        solar_obj=None,
        lunar_obj=None,
        ba_obj=None,
    ):
        self.pillars = pillars
        self.is_female = is_female
        self.solar = solar_obj
        self.lunar = lunar_obj
        self.ba = ba_obj
        self.me = pillars.me
        self.gans = pillars.gans
        self.zhis = pillars.zhis
        self.zhus = pillars.zhus

        # 计算所有基础数据
        self._calc_shishen()
        self._calc_scores()
        self._calc_strength()
        self._calc_dayun()
        self._calc_temps()
        self._calc_relations()
        self._calc_zangfu()
        self._calc_lu_and_special()

    # ─── 十神计算 ───────────────────────────────────────────

    def _calc_shishen(self):
        """计算十神。"""
        me = self.me
        # 天干十神
        self.gan_shens = []
        for seq, item in enumerate(self.gans):
            if seq == 2:
                self.gan_shens.append('--')
            else:
                self.gan_shens.append(SHI_SHEN[me][item])

        # 地支主气十神
        self.zhi_shens = []
        for item in self.zhis:
            d = CANG_GAN[item]
            self.zhi_shens.append(SHI_SHEN[me][max(d, key=d.get)])

        self.shens = self.gan_shens + self.zhi_shens

        # 地支所有神（混合列表）
        self.zhi_shens2 = []
        # 地支所有神（每柱字符串）
        self.zhi_shen3 = []
        for item in self.zhis:
            d = CANG_GAN[item]
            tmp = ''
            for item2 in d:
                self.zhi_shens2.append(SHI_SHEN[me][item2])
                tmp += SHI_SHEN[me][item2]
            self.zhi_shen3.append(tmp)

        self.shens2 = self.gan_shens + self.zhi_shens2

        # 十二长生状态
        self.statuses = [SHI_SHEN[me][item] for item in self.zhis]

        # 十神柱组合
        self.shen_zhus = list(
            zip(self.gan_shens, self.zhi_shens, strict=False),
        )

    # ─── 五行分数 ───────────────────────────────────────────

    def _calc_scores(self):
        """计算五行分数和十干分数。"""
        self.scores = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        self.gan_scores = {
            '甲': 0,
            '乙': 0,
            '丙': 0,
            '丁': 0,
            '戊': 0,
            '己': 0,
            '庚': 0,
            '辛': 0,
            '壬': 0,
            '癸': 0,
        }

        for item in self.gans:
            self.scores[GAN_5[item]] += 5
            self.gan_scores[item] += 5

        # 地支 + 月支加倍
        for item in [*list(self.zhis), self.zhis[1]]:
            for gan in CANG_GAN[item]:
                self.scores[GAN_5[gan]] += CANG_GAN[item][gan]
                self.gan_scores[gan] += CANG_GAN[item][gan]

    # ─── 强弱判断 ───────────────────────────────────────────

    def _calc_strength(self):
        """计算八字强弱。"""
        me = self.me
        # 子平真诠的计算
        self.weak = True
        self.me_status = []
        for item in self.zhis:
            self.me_status.append(SHI_SHEN[me][item])
            if SHI_SHEN[me][item] in ('长', '帝', '建'):
                self.weak = False

        if self.weak:
            if self.shens.count('比') + self.me_status.count('库') > 2:
                self.weak = False

        # 网上的计算
        me_attrs_ = SHI_SHEN[me].inverse
        self.strong = (
            self.gan_scores[me_attrs_['比']]
            + self.gan_scores[me_attrs_['劫']]
            + self.gan_scores[me_attrs_['枭']]
            + self.gan_scores[me_attrs_['印']]
        )

    # ─── 大运计算 ───────────────────────────────────────────

    def _calc_dayun(self):
        """计算大运。"""
        self.direction = calc_direction(self.gans[0], self.is_female)
        self.dayuns = calc_dayun_ganzhi(
            self.gans[1],
            self.zhis[1],
            self.direction,
        )

    # ─── 温湿度计算 ─────────────────────────────────────────

    def _calc_temps(self):
        """计算温湿度。"""
        self.temps_scores = (
            TEMPERATURE[self.gans[0]]
            + TEMPERATURE[self.gans[1]]
            + TEMPERATURE[self.me]
            + TEMPERATURE[self.gans[3]]
            + TEMPERATURE[self.zhis[0]]
            + TEMPERATURE[self.zhis[1]] * 2
            + TEMPERATURE[self.zhis[2]]
            + TEMPERATURE[self.zhis[3]]
        )

    # ─── 地支关系计算 ───────────────────────────────────────

    def _calc_relations(self):
        """计算四柱间的地支关系和天干合。"""
        self.zhi_6he = calc_zhi_6he(self.zhis)
        self.zhi_6chong = calc_zhi_6chong(self.zhis)
        self.gan_he = calc_gan_he_list(self.gans)
        self.zhi_xing = calc_zhi_xing(self.zhis)
        self.gongs = get_gong(self.gans, self.zhis)

    # ─── 脏腑计算 ───────────────────────────────────────────

    def _calc_zangfu(self):
        """计算脏腑。"""
        self.zangs = OrderedDict([
            ('胆', 0),
            ('肝', 0),
            ('小肠', 0),
            ('心', 0),
            ('胃', 0),
            ('脾', 0),
            ('大肠', 0),
            ('肺', 0),
            ('膀胱', 0),
            ('肾', 0),
            ('三焦', 0),
            ('心包', 0),
        ])
        for item in self.gans:
            self.zangs[NEI_ZANG_GAN[item]] += 1
        for item in self.zhis:
            self.zangs[NEI_ZANG_ZHI[item]] += 1

    # ─── 各种特殊计算 ───────────────────────────────────────

    def _calc_lu_and_special(self):
        """计算禄、库、各种特殊天干。"""
        me = self.me
        inv = SHI_SHEN[me].inverse

        self.me_lu = inv['建']
        self.me_jue = inv['绝']
        self.me_tai = inv['胎']
        self.me_di = inv['帝']

        self.shang = inv['伤']
        self.shang_lu = SHI_SHEN[self.shang].inverse['建']
        self.shang_di = SHI_SHEN[self.shang].inverse['帝']

        self.yin = inv['印']
        self.yin_lu = SHI_SHEN[self.yin].inverse['建']
        self.xiao = inv['枭']
        self.xiao_lu = SHI_SHEN[self.xiao].inverse['建']

        self.cai = inv['财']
        self.cai_lu = SHI_SHEN[self.cai].inverse['建']
        self.cai_di = SHI_SHEN[self.cai].inverse['帝']
        self.piancai = inv['才']
        self.piancai_lu = SHI_SHEN[self.piancai].inverse['建']
        self.piancai_di = SHI_SHEN[self.piancai].inverse['帝']

        self.guan = inv['官']
        self.guan_lu = SHI_SHEN[self.guan].inverse['建']
        self.guan_di = SHI_SHEN[self.guan].inverse['帝']
        self.sha = inv['杀']
        self.sha_lu = SHI_SHEN[self.sha].inverse['建']
        self.sha_di = SHI_SHEN[self.sha].inverse['帝']

        self.jie = inv['劫']
        self.shi = inv['食']
        self.shi_lu = SHI_SHEN[self.shi].inverse['建']
        self.shi_di = SHI_SHEN[self.shi].inverse['帝']

        self.me_ku = SHI_SHEN[me]['库'][0]
        self.cai_ku = SHI_SHEN[self.cai]['库'][0]
        self.guan_ku = SHI_SHEN[self.guan]['库'][0]
        self.yin_ku = SHI_SHEN[self.yin]['库'][0]
        self.shi_ku = SHI_SHEN[self.shi]['库'][0]

    # ─── 数据导出方法 ───────────────────────────────────────

    def get_pillar_detail(self, seq: int) -> dict:
        """获取某柱的详细信息。"""
        gan = self.gans[seq]
        zhi = self.zhis[seq]
        me = self.me
        day_zhu = self.zhus[2]

        # 藏干详情
        canggan = [
            {
                'gan': cg,
                'wuxing': GAN_5[cg],
                'shishen': SHI_SHEN[me][cg],
                'score': CANG_GAN[zhi][cg],
            }
            for cg in CANG_GAN[zhi]
        ]

        # 地支关系
        zhi_rels = {}
        others = list(self.zhis[:seq]) + list(self.zhis[seq + 1 :])
        for type_ in ZHI_ATTR[zhi]:
            matched = []
            target = ZHI_ATTR[zhi][type_]
            if isinstance(target, str):
                if target in others:
                    matched.append(target)
            elif isinstance(target, tuple):
                matched.extend(z for z in target if z in others)
            if matched:
                zhi_rels[type_] = matched

        # 各柱对本柱地支的十神
        cross_shens = {}
        for i, g in enumerate(self.gans):
            pos = ['年', '月', '日', '时'][i]
            cross_shens[pos] = SHI_SHEN[g][zhi]

        return {
            'position': ['年', '月', '日', '时'][seq],
            'gan': gan,
            'zhi': zhi,
            'gan_yinyang': yinyang(gan),
            'zhi_yinyang': yinyang(zhi),
            'gan_wuxing': GAN_5[gan],
            'zhi_wuxing': WU_XING_ZHI[zhi],
            'gan_shishen': self.gan_shens[seq],
            'zhi_shishen': self.zhi_shens[seq],
            'zhi_all_shishen': self.zhi_shen3[seq],
            'twelve_stage': SHI_SHEN[me][zhi],
            'gan_relations': check_gan(gan, self.gans),
            'zhi_relations': zhi_rels,
            'cross_shishen': cross_shens,
            'canggan': canggan,
            'nayin': NA_YIN.get((gan, zhi), ''),
            'kong_wang': is_kong_wang(day_zhu, zhi) if seq != 2 else False,
            'gen': get_gen(gan, self.zhis),
            'ganzhi_relation': RELATION.get(
                (GAN_5[gan], WU_XING_ZHI[zhi]),
                '',
            ),
            'ganzhi_he': gan_zhi_he(gan, zhi),
            'TEMPERATURE': {'gan': TEMPERATURE[gan], 'zhi': TEMPERATURE[zhi]},
        }

    def get_siling(self) -> dict:
        """获取四令信息。"""
        return XIU_QIU.get(self.zhis[1], {})

    def get_wuxing_scores(self) -> dict:
        """获取五行分数详情。"""
        return {
            'scores': dict(self.scores),
            'gan_scores': dict(self.gan_scores),
            'strong_value': self.strong,
            'mid_value': 29,
            'has_strong_root': not self.weak,
            'temps_scores': self.temps_scores,
            'gong': self.gongs,
        }

    def get_zangfu(self) -> dict:
        """获取脏腑数据。"""
        return dict(self.zangs)

    def get_liuqin(self) -> dict:
        """获取六亲数据。"""
        is_female = self.is_female
        liuqins = bidict({
            '才': '父亲',
            '财': '财' if is_female else '妻',
            '印': '母亲',
            '枭': '偏印' if is_female else '祖父',
            '官': '丈夫' if is_female else '女儿',
            '杀': '情夫' if is_female else '儿子',
            '劫': '兄弟' if is_female else '姐妹',
            '比': '姐妹' if is_female else '兄弟',
            '食': '女儿' if is_female else '下属',
            '伤': '儿子' if is_female else '孙女',
        })

        result = {}
        for item in TIAN_GAN:
            shishen = SHI_SHEN[self.me][item]
            statuses = [SHI_SHEN[item][z] for z in self.zhis]
            result[item] = {
                'shishen': shishen,
                'liuqin': liuqins[shishen],
                'statuses': {
                    '年': statuses[0],
                    '月': statuses[1],
                    '日': statuses[2],
                    '时': statuses[3],
                },
            }
        return result


def create_from_solar(
    year: int,
    month: int,
    day: int,
    hour: int,
    tz: int = 8,
) -> tuple:
    """从公历创建 Solar/Lunar/八字对象。"""
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    ba = lunar.getEightChar()
    gans = (
        ba.getYearGan(),
        ba.getMonthGan(),
        ba.getDayGan(),
        ba.getTimeGan(),
    )
    zhis = (
        ba.getYearZhi(),
        ba.getMonthZhi(),
        ba.getDayZhi(),
        ba.getTimeZhi(),
    )
    return FourPillars(gans, zhis), solar, lunar, ba


def create_from_lunar(
    year: int,
    month: int,
    day: int,
    hour: int,
    tz: int = 8,
    is_leap_month: bool = False,
) -> tuple:
    """从农历创建 Solar/Lunar/八字对象。"""
    month_ = month * -1 if is_leap_month else month
    lunar = Lunar.fromYmdHms(year, month_, day, hour, 0, 0)
    solar = lunar.getSolar()
    ba = lunar.getEightChar()
    gans = (
        ba.getYearGan(),
        ba.getMonthGan(),
        ba.getDayGan(),
        ba.getTimeGan(),
    )
    zhis = (
        ba.getYearZhi(),
        ba.getMonthZhi(),
        ba.getDayZhi(),
        ba.getTimeZhi(),
    )
    return FourPillars(gans, zhis), solar, lunar, ba


def create_from_bazi(
    year_gz: str,
    month_gz: str,
    day_gz: str,
    time_gz: str,
) -> tuple:
    """从八字干支直接创建。"""
    gans = (year_gz[0], month_gz[0], day_gz[0], time_gz[0])
    zhis = (year_gz[1], month_gz[1], day_gz[1], time_gz[1])
    return FourPillars(gans, zhis), None, None, None
