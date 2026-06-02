"""
八字合婚引擎
============
比较两个人的八字，分析匹配度。

四个维度：
  1. 年柱生肖冲合（根基）
  2. 日支冲合（夫妻宫）
  3. 五行互补性（用神）
  4. 十神匹配（女官男财）

用法:
  from api.paipan.hehun import HehunEngine
  engine = HehunEngine()
  report = engine.analyze(male_bazi, female_bazi)
"""

from dataclasses import dataclass, field
from .data.ganzhi import ZHI_CHONG, ZHI_HE, ZHI_XING, ZHI_HAI, GAN_HE, get_shishen


# 生肖六合配对
SHENGXIAO_HE = {
    ("子","丑"):("鼠","牛","子丑合土，天生互补"),
    ("寅","亥"):("虎","猪","寅亥合木，志同道合"),
    ("卯","戌"):("兔","狗","卯戌合火，热情相投"),
    ("辰","酉"):("龙","鸡","辰酉合金，龙凤呈祥"),
    ("巳","申"):("蛇","猴","巳申合水，智慧相配"),
    ("午","未"):("马","羊","午未合土，温柔和谐"),
}

# 生肖六冲
SHENGXIAO_CHONG = {
    ("子","午"):("鼠","马","子午相冲，性格差异大"),
    ("丑","未"):("牛","羊","丑未相冲，意见常不合"),
    ("寅","申"):("虎","猴","寅申相冲，各有主见"),
    ("卯","酉"):("兔","鸡","卯酉相冲，观念冲突"),
    ("辰","戌"):("龙","狗","辰戌相冲，易有争执"),
    ("巳","亥"):("蛇","猪","巳亥相冲，生活方式不同"),
}


@dataclass
class HehunReport:
    """合婚报告"""
    # 双方基本信息
    male_name: str
    female_name: str
    male_bazi: str
    female_bazi: str
    male_rizhu: str
    female_rizhu: str

    # 各维度评分
    nianzhu_score: int = 0       # 年柱分 (满分20)
    nianzhu_detail: str = ""
    rizhi_score: int = 0         # 日支分 (满分30)
    rizhi_detail: str = ""
    wuxing_score: int = 0        # 五行分 (满分20)
    wuxing_detail: str = ""
    shishen_score: int = 0       # 十神分 (满分10)
    shishen_detail: str = ""

    # 总分
    total_score: int = 0         # 满分80
    level: str = ""              # 上等婚/中等婚/一般/需谨慎
    summary: str = ""


class HehunEngine:
    """合婚引擎"""

    def analyze(self, male, female, male_name="男方", female_name="女方") -> HehunReport:
        """分析两人八字匹配度"""
        report = HehunReport(
            male_name=male_name,
            female_name=female_name,
            male_bazi=f"{male.year.gan}{male.year.zhi} {male.month.gan}{male.month.zhi} {male.day.gan}{male.day.zhi} {male.hour.gan}{male.hour.zhi}",
            female_bazi=f"{female.year.gan}{female.year.zhi} {female.month.gan}{female.month.zhi} {female.day.gan}{female.day.zhi} {female.hour.gan}{female.hour.zhi}",
            male_rizhu=f"{male.rizhu}({male.rizhu_wuxing})",
            female_rizhu=f"{female.rizhu}({female.rizhu_wuxing})",
        )

        # 1. 年柱生肖冲合（20分）
        self._analyze_nianzhu(report, male.year.zhi, female.year.zhi)

        # 2. 日支冲合（30分）
        self._analyze_rizhi(report, male.day.zhi, female.day.zhi)

        # 3. 五行互补（20分）
        self._analyze_wuxing(report, male, female)

        # 4. 十神匹配（10分）
        self._analyze_shishen(report, male, female)

        # 5. 综合
        report.total_score = (report.nianzhu_score + report.rizhi_score +
                              report.wuxing_score + report.shishen_score)

        if report.total_score >= 60:
            report.level = "上等婚配"
        elif report.total_score >= 40:
            report.level = "中等婚配"
        elif report.total_score >= 25:
            report.level = "一般婚配"
        else:
            report.level = "需谨慎"

        report.summary = self._generate_summary(report)

        return report

    def _analyze_nianzhu(self, report: HehunReport, m_zhi: str, f_zhi: str):
        """年柱分析"""
        pair = (m_zhi, f_zhi)
        pair_rev = (f_zhi, m_zhi)

        # 六合
        for (a, b), (sx1, sx2, desc) in SHENGXIAO_HE.items():
            if pair == (a, b) or pair == (b, a):
                report.nianzhu_score = 20
                report.nianzhu_detail = f"生肖{sx1}与{sx2}六合——{desc}。年柱根基相合，大吉。"
                return

        # 六冲
        for (a, b), (sx1, sx2, desc) in SHENGXIAO_CHONG.items():
            if pair == (a, b) or pair == (b, a):
                report.nianzhu_score = -10
                report.nianzhu_detail = f"生肖{sx1}与{sx2}六冲——{desc}。年柱根基相冲，需多加磨合。"
                return

        # 三合
        sanhe_groups = [
            (["申","子","辰"], "水局"),
            (["亥","卯","未"], "木局"),
            (["寅","午","戌"], "火局"),
            (["巳","酉","丑"], "金局"),
        ]
        for zhis, name in sanhe_groups:
            if m_zhi in zhis and f_zhi in zhis and m_zhi != f_zhi:
                report.nianzhu_score = 15
                report.nianzhu_detail = f"生肖同属{name}，三合有情，年柱根基良好。"
                return

        # 无冲无合
        report.nianzhu_score = 5
        report.nianzhu_detail = "生肖无冲无合，年柱根基平平。"

    def _analyze_rizhi(self, report: HehunReport, m_zhi: str, f_zhi: str):
        """日支（夫妻宫）分析"""
        # 六合
        if ZHI_HE.get((m_zhi, f_zhi)):
            report.rizhi_score = 30
            report.rizhi_detail = f"日支{m_zhi}与{f_zhi}六合，夫妻宫相合，婚姻根基稳固。"
            return

        # 六冲
        if ZHI_CHONG.get(m_zhi) == f_zhi:
            report.rizhi_score = -15
            report.rizhi_detail = f"日支{m_zhi}与{f_zhi}六冲，夫妻宫相冲，需更多理解包容。"
            return

        # 三合
        sanhe_map = {
            ("申","子"):"水",("子","辰"):"水",("申","辰"):"水",
            ("亥","卯"):"木",("卯","未"):"木",("亥","未"):"木",
            ("寅","午"):"火",("午","戌"):"火",("寅","戌"):"火",
            ("巳","酉"):"金",("酉","丑"):"金",("巳","丑"):"金",
        }
        for (a,b), wx in sanhe_map.items():
            if (m_zhi==a and f_zhi==b) or (m_zhi==b and f_zhi==a):
                report.rizhi_score = 25
                report.rizhi_detail = f"日支{m_zhi}与{f_zhi}三合{wx}局，夫妻同心。"
                return

        # 同五行
        from .data.ganzhi import ZHI_WUXING
        if ZHI_WUXING.get(m_zhi) == ZHI_WUXING.get(f_zhi):
            report.rizhi_score = 15
            report.rizhi_detail = f"日支{m_zhi}与{f_zhi}同五行，志趣相投。"
            return

        report.rizhi_score = 5
        report.rizhi_detail = "日支无冲无合，夫妻宫平平。"

    def _analyze_wuxing(self, report: HehunReport, male, female):
        """五行互补分析"""
        m_scores = male.wuxing_scores
        f_scores = female.wuxing_scores

        # 比较双方最强和最弱的五行
        m_weak = min(m_scores, key=m_scores.get)
        m_strong = max(m_scores, key=m_scores.get)
        f_weak = min(f_scores, key=f_scores.get)
        f_strong = max(f_scores, key=f_scores.get)

        score = 10
        details = []

        # 你能补我弱的
        WUXING_SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
        for wx_s, wx_bs in WUXING_SHENG.items():
            if f_strong == wx_s and m_weak == wx_bs:
                score += 5
                details.append(f"女方{f_strong}旺可补男方{m_weak}弱")
            if m_strong == wx_s and f_weak == wx_bs:
                score += 5
                details.append(f"男方{m_strong}旺可补女方{f_weak}弱")

        # 同五行加分
        if m_strong == f_strong:
            details.append(f"双方均以{m_strong}为强，志趣相投但需防竞争")

        report.wuxing_score = min(20, max(0, score))
        report.wuxing_detail = "；".join(details) if details else "五行无显著互补关系"

    def _analyze_shishen(self, report: HehunReport, male, female):
        """十神匹配分析"""
        score = 5
        details = []

        # 男命财星 vs 女命官星
        male_cai = get_shishen(male.rizhu, female.rizhu)
        female_guan = get_shishen(female.rizhu, male.rizhu)

        if male_cai in ("正财", "偏财"):
            score += 3
            details.append(f"女方日主对男方为{male_cai}，传统认为女为男之财，吉")

        if female_guan in ("正官", "七杀"):
            score += 2
            details.append(f"男方日主对女方为{female_guan}，传统认为男为女之官，吉")

        report.shishen_score = min(10, score)
        report.shishen_detail = "；".join(details) if details else "十神无特殊匹配"

    def _generate_summary(self, report: HehunReport) -> str:
        """生成综合评语"""
        parts = [
            f"{report.male_name}八字：{report.male_bazi}，日主{report.male_rizhu}。",
            f"{report.female_name}八字：{report.female_bazi}，日主{report.female_rizhu}。",
            f"合婚总分{report.total_score}/80，{report.level}。",
        ]

        highlights = []
        if report.nianzhu_score >= 15:
            highlights.append("年柱根基深厚")
        if report.rizhi_score >= 25:
            highlights.append("夫妻宫相合")
        if report.wuxing_score >= 15:
            highlights.append("五行互补性强")

        warnings = []
        if report.nianzhu_score < 0:
            warnings.append("年柱相冲")
        if report.rizhi_score < 0:
            warnings.append("夫妻宫相冲")

        if highlights:
            parts.append("优势：" + "、".join(highlights) + "。")
        if warnings:
            parts.append("注意：" + "、".join(warnings) + "，需多磨合包容。")

        parts.append("以上基于传统命理视角，仅供参考。婚姻幸福在于双方经营，八字合婚仅为传统文化参考。")

        return "".join(parts)
