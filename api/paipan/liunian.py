"""
流年/流月推算引擎
=================
基于出生八字的流年流月分析。

原理：每年的干支（流年）与命局四柱发生十神+冲合关系，
     产生不同的吉凶影响。流月同理。

用法:
  from api.paipan.liunian import LiunianEngine
  engine = LiunianEngine()
  year_report = engine.calc_liunian(bazi_result, 2026)
"""

from dataclasses import dataclass, field
from lunar_python import Solar
from .data.ganzhi import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    get_shishen, get_changsheng_stage, is_yang,
    ZHI_HE, ZHI_CHONG, ZHI_XING, ZHI_HAI, GAN_HE,
)


@dataclass
class LiunianReport:
    """单年流年报告"""
    year: int
    year_gan: str
    year_zhi: str
    year_ganzhi: str
    year_shengxiao: str
    nayin: str

    # 与四柱的关系
    shishen_to_rizhu: str           # 年干对日主的十神
    shishen_desc: str               # 十神含义
    chong_pillars: list = field(default_factory=list)   # 冲哪些柱
    he_pillars: list = field(default_factory=list)      # 合哪些柱
    xing_pillars: list = field(default_factory=list)    # 刑哪些柱

    # 综合评估
    overall: str = ""               # 总体运势简述
    career: str = ""                # 事业
    wealth: str = ""                # 财运
    health: str = ""                # 健康
    relationship: str = ""          # 感情


@dataclass
class LiumonthReport:
    """单月流月报告"""
    year: int
    month: int
    month_gan: str
    month_zhi: str
    month_ganzhi: str
    shishen_to_rizhu: str
    keywords: list = field(default_factory=list)  # 关键词


class LiunianEngine:
    """流年推算引擎"""

    # 十神简释
    SHISHEN_DESC = {
        "比肩": "自我意识增强，宜独立行事",
        "劫财": "竞争较多，注意人际关系和开销",
        "食神": "才华展现，适合创作和学习",
        "伤官": "表达欲强，注意言行分寸",
        "正财": "财运稳定，适合投资理财",
        "偏财": "意外之财，但来去较快",
        "正官": "事业运佳，可能升职或有贵人",
        "七杀": "压力增大，挑战与机遇并存",
        "正印": "学习运佳，可能有贵人相助",
        "偏印": "特殊技能提升，但注意偏执",
    }

    def calc_liunian(self, bazi, year: int) -> LiunianReport:
        """
        计算某年的流年运势。

        Args:
            bazi: BaziResult 对象
            year: 公历年份
        """
        # 1. 获取流年干支
        solar = Solar.fromYmdHms(year, 6, 1, 12, 0, 0)  # 年中
        lunar = solar.getLunar()
        ba = lunar.getEightChar()

        year_gan = ba.getYearGan()
        year_zhi = ba.getYearZhi()
        year_ganzhi = year_gan + year_zhi

        # 生肖
        sx_map = {"子":"鼠","丑":"牛","寅":"虎","卯":"兔","辰":"龙","巳":"蛇",
                  "午":"马","未":"羊","申":"猴","酉":"鸡","戌":"狗","亥":"猪"}
        sx = sx_map.get(year_zhi, "")

        # 纳音
        from .data.ganzhi import get_nayin
        nayin = get_nayin(year_gan, year_zhi)

        # 2. 年干对日主的十神
        shishen = get_shishen(bazi.rizhu, year_gan)

        # 3. 年支与四柱地支的关系
        chong = []
        he = []
        xing = []
        positions = ["年", "月", "日", "时"]
        bazi_zhi = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

        for pos, zhi in zip(positions, bazi_zhi):
            if ZHI_CHONG.get(year_zhi) == zhi:
                chong.append(f"{pos}柱")
            if ZHI_HE.get((year_zhi, zhi)):
                he.append(f"{pos}柱({year_zhi}{zhi}合)")
            if ZHI_XING.get(year_zhi) == zhi or ZHI_XING.get(zhi) == year_zhi:
                xing.append(f"{pos}柱")

        # 4. 综合评估
        report = LiunianReport(
            year=year,
            year_gan=year_gan,
            year_zhi=year_zhi,
            year_ganzhi=year_ganzhi,
            year_shengxiao=sx,
            nayin=nayin,
            shishen_to_rizhu=shishen,
            shishen_desc=self.SHISHEN_DESC.get(shishen, ""),
            chong_pillars=chong,
            he_pillars=he,
            xing_pillars=xing,
        )

        # 5. 逐项分析
        report.overall = self._analyze_overall(report, bazi)
        report.career = self._analyze_career(report, bazi)
        report.wealth = self._analyze_wealth(report, bazi)
        report.health = self._analyze_health(report)
        report.relationship = self._analyze_relationship(report)

        return report

    def _analyze_overall(self, r: LiunianReport, bazi) -> str:
        """总体运势"""
        parts = [f"{r.year}年为{r.year_ganzhi}年（{r.year_shengxiao}年），纳音{r.nayin}。"]
        parts.append(f"流年天干{r.year_gan}对日主{bazi.rizhu}为{r.shishen_to_rizhu}——{r.shishen_desc}。")

        if r.chong_pillars:
            parts.append(f"流年地支{r.year_zhi}与{'、'.join(r.chong_pillars)}相冲，主变动较大，需注意稳定性。")
        elif r.he_pillars:
            parts.append(f"流年与{'、'.join(r.he_pillars)}，主和谐顺利。")

        if r.shishen_to_rizhu in ("正官", "正印", "正财", "食神"):
            parts.append("总体而言，此年对你较为有利，宜积极进取。")
        elif r.shishen_to_rizhu in ("七杀", "劫财", "伤官"):
            parts.append("此年挑战与机遇并存，宜谨慎行事，稳扎稳打。")
        else:
            parts.append("此年较为平稳，宜按部就班。")

        return "".join(parts)

    def _analyze_career(self, r: LiunianReport, bazi) -> str:
        """事业分析"""
        if r.shishen_to_rizhu in ("正官", "七杀"):
            return f"流年{r.shishen_to_rizhu}当值，事业上有{'晋升机遇' if r.shishen_to_rizhu == '正官' else '较大压力'}，宜{'主动承担责任' if r.shishen_to_rizhu == '正官' else '沉着应对挑战'}。"
        if r.shishen_to_rizhu in ("正印", "偏印"):
            return f"流年印星当值，利于学习进修和考取证照，{'正印主正统学历' if r.shishen_to_rizhu == '正印' else '偏印主特殊技能'}。"
        if r.shishen_to_rizhu in ("食神", "伤官"):
            return f"流年食伤吐秀，创造力强，适合发挥专业才能，{r.shishen_to_rizhu}主{'稳定输出' if r.shishen_to_rizhu == '食神' else '突破创新'}。"
        return "事业运势平稳，宜做好本职工作，等待时机。"

    def _analyze_wealth(self, r: LiunianReport, bazi) -> str:
        """财运分析"""
        if r.shishen_to_rizhu in ("正财", "偏财"):
            return f"流年{r.shishen_to_rizhu}当值，财运{'稳健上升，宜储蓄' if r.shishen_to_rizhu == '正财' else '有意外之喜，但来去较快，宜见好就收'}。"
        if r.shishen_to_rizhu == "食神":
            return "食神生财，以专业技能或创意带来收入，宜脚踏实地。"
        if r.shishen_to_rizhu in ("劫财", "比肩"):
            return "比劫当值，开销增大，注意合伙纠纷和冲动消费。"
        return "财运平稳，无大起大落。"

    def _analyze_health(self, r: LiunianReport) -> str:
        """健康分析"""
        if r.chong_pillars:
            return f"流年冲{'、'.join(r.chong_pillars)}，需注意{'父母长辈健康' if '年柱' in str(r.chong_pillars) else '自身健康' if '日柱' in str(r.chong_pillars) else '身体保养'}。"
        return "健康运势平稳，注意作息规律即可。"

    def _analyze_relationship(self, r: LiunianReport) -> str:
        """感情分析"""
        if r.shishen_to_rizhu == "正官" or r.shishen_to_rizhu == "正财":
            return f"流年{r.shishen_to_rizhu}当值，{'利于婚姻和正式关系' if r.shishen_to_rizhu == '正官' else '感情稳定，适合谈婚论嫁'}。"
        if "桃花" in str(r.he_pillars):
            return "流年桃花旺盛，单身者有机会遇到心仪对象。"
        if r.shishen_to_rizhu == "劫财":
            return "劫财年份注意感情中的竞争和口舌。"
        return "感情运平稳，顺其自然即可。"

    def calc_liumonth(self, bazi, year: int, month: int) -> LiumonthReport:
        """计算某年某月的流月运势"""
        solar = Solar.fromYmdHms(year, month, 15, 12, 0, 0)
        lunar = solar.getLunar()
        ba = lunar.getEightChar()

        m_gan = ba.getMonthGan()
        m_zhi = ba.getMonthZhi()
        shishen = get_shishen(bazi.rizhu, m_gan)

        keywords = []
        if ZHI_CHONG.get(m_zhi) == bazi.day.zhi:
            keywords.append("日支逢冲，宜静不宜动")
        if ZHI_HE.get((m_zhi, bazi.day.zhi)):
            keywords.append("日支逢合，利于合作")

        if shishen in ("正官", "正财", "正印"):
            keywords.append(f"月干{shishen}当令，利于{'事业' if shishen=='正官' else '财运' if shishen=='正财' else '学习'}")

        return LiumonthReport(
            year=year, month=month,
            month_gan=m_gan, month_zhi=m_zhi,
            month_ganzhi=m_gan + m_zhi,
            shishen_to_rizhu=shishen,
            keywords=keywords,
        )


def calc_2026_liunian(bazi) -> LiunianReport:
    """计算2026年（丙午年）流年运势"""
    engine = LiunianEngine()
    return engine.calc_liunian(bazi, 2026)
