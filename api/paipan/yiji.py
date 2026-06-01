"""
今日宜忌引擎
============
基于建除十二神、黄道黑道、个人八字冲合的宜忌分析。

所有规则来自《协纪辨方书》，纯代码实现，不靠AI。

用法:
  from api.paipan.yiji import DailyYiji
  yj = DailyYiji()
  result = yj.analyze(today_solar, user_bazi_result)
"""

from datetime import datetime
from dataclasses import dataclass, field
from lunar_python import Solar, Lunar

from .data.ganzhi import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    GAN_HE, ZHI_HE, ZHI_CHONG, ZHI_XING, ZHI_HAI,
)

# ===== 建除十二神 =====
# 正月建寅, 二月建卯... 从月建起顺数到日支
JIANCHU = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]

# 建除十二神的通用宜忌
JIANCHU_YIJI = {
    "建": {"yi": [], "ji": ["动土", "开仓"], "desc": "建日，万物开始，宜出行、上任"},
    "除": {"yi": ["扫除", "治病", "去旧"], "ji": ["嫁娶", "开业"], "desc": "除日，除旧布新，宜大扫除"},
    "满": {"yi": ["祭祀", "祈福"], "ji": ["开新", "动土", "嫁娶"], "desc": "满日，满则溢，宜收尾不宜开新"},
    "平": {"yi": ["出行", "修造"], "ji": [], "desc": "平日，诸事平稳，百无禁忌"},
    "定": {"yi": ["订婚", "签约", "入学"], "ji": ["诉讼"], "desc": "定日，宜定盟约，忌争讼"},
    "执": {"yi": ["捕捉", "讨债"], "ji": ["出行", "搬家"], "desc": "执日，宜擒拿讨债，不宜远行"},
    "破": {"yi": ["拆屋", "治病"], "ji": ["嫁娶", "开业", "出行"], "desc": "破日，大耗之日，百事不宜"},
    "危": {"yi": ["祭祀", "安葬"], "ji": ["嫁娶", "远行"], "desc": "危日，宜谨慎行事"},
    "成": {"yi": ["嫁娶", "开业", "出行", "签约"], "ji": ["诉讼"], "desc": "成日，诸事可成，大吉之日"},
    "收": {"yi": ["收藏", "入库", "纳财"], "ji": ["出行", "安葬"], "desc": "收日，宜收纳不宜发散"},
    "开": {"yi": ["开业", "出行", "嫁娶", "动土"], "ji": ["安葬"], "desc": "开日，开门纳吉，大吉之日"},
    "闭": {"yi": ["祭祀", "安葬", "收藏"], "ji": ["开业", "出行", "动土"], "desc": "闭日，宜收敛不宜开创"},
}

# ===== 黄道黑道 =====
# 以日支查：青龙/明堂/天刑/朱雀/金匮/天德/白虎/玉堂/天牢/玄武/司命/勾陈
# 口诀: 子午青龙起在申, 卯酉之日又在寅, 寅申须从子上起, 巳亥在午不须论, 唯有辰戌归辰位, 丑未原从戌上寻
HUANGDAO_START = {
    "子": 8, "午": 8,   # 申(8)
    "卯": 2, "酉": 2,   # 寅(2)
    "寅": 0, "申": 0,   # 子(0)
    "巳": 6, "亥": 6,   # 午(6)
    "辰": 4, "戌": 4,   # 辰(4)
    "丑": 10, "未": 10,  # 戌(10)
}

# 十二神顺序（黄道吉日 / 黑道凶日）
HUANGDAO_SHEN = [
    ("青龙", "黄道"), ("明堂", "黄道"), ("天刑", "黑道"),
    ("朱雀", "黑道"), ("金匮", "黄道"), ("天德", "黄道"),
    ("白虎", "黑道"), ("玉堂", "黄道"), ("天牢", "黑道"),
    ("玄武", "黑道"), ("司命", "黄道"), ("勾陈", "黑道"),
]

# 彭祖百忌（日干/日支忌）
PENGZU_JI = {
    # 日干忌
    "甲": "不开仓", "乙": "不栽植", "丙": "不修灶", "丁": "不剃头",
    "戊": "不受田", "己": "不破券", "庚": "不经络", "辛": "不合酱",
    "壬": "不决水", "癸": "不词讼",
    # 日支忌
    "子": "不问卜", "丑": "不冠带", "寅": "不祭祀", "卯": "不穿井",
    "辰": "不哭泣", "巳": "不远行", "午": "不苫盖", "未": "不服药",
    "申": "不安床", "酉": "不会客", "戌": "不吃犬", "亥": "不嫁娶",
}


@dataclass
class YijiResult:
    """宜忌分析结果"""
    date: str
    day_ganzhi: str
    day_gan: str
    day_zhi: str
    jianchu: str
    jianchu_desc: str
    huangdao_shen: str
    huangdao_type: str  # "黄道" or "黑道"
    pengzu_ji: list

    # 通用宜忌
    general_yi: list = field(default_factory=list)
    general_ji: list = field(default_factory=list)

    # 个人维度（需要用户八字）
    personal_yi: list = field(default_factory=list)
    personal_ji: list = field(default_factory=list)
    personal_analysis: str = ""


class DailyYiji:
    """每日宜忌分析器"""

    def analyze(self, solar: Solar, user_bazi=None) -> YijiResult:
        """
        分析今日宜忌。

        Args:
            solar: lunar_python Solar 对象
            user_bazi: api.paipan.BaziResult 对象（可选，用于个人分析）

        Returns:
            YijiResult: 完整的宜忌结果
        """
        lunar = solar.getLunar()
        ba = lunar.getEightChar()

        day_gan = ba.getDayGan()
        day_zhi = ba.getDayZhi()
        day_ganzhi = day_gan + day_zhi

        month_zhi = ba.getMonthZhi()

        # 1. 建除十二神
        jianchu = self._calc_jianchu(month_zhi, day_zhi)

        # 2. 黄道黑道
        hd_shen, hd_type = self._calc_huangdao(day_zhi)

        # 3. 彭祖百忌
        pengzu = self._calc_pengzu(day_gan, day_zhi)

        # 4. 通用宜忌
        gen_yi, gen_ji = self._calc_general_yiji(jianchu, hd_type)

        result = YijiResult(
            date=solar.toFullString(),
            day_ganzhi=day_ganzhi,
            day_gan=day_gan,
            day_zhi=day_zhi,
            jianchu=jianchu,
            jianchu_desc=JIANCHU_YIJI.get(jianchu, {}).get("desc", ""),
            huangdao_shen=hd_shen,
            huangdao_type=hd_type,
            pengzu_ji=pengzu,
            general_yi=gen_yi,
            general_ji=gen_ji,
        )

        # 5. 个人分析（如果提供了用户八字）
        if user_bazi is not None:
            self._add_personal_analysis(result, user_bazi)

        return result

    def _calc_jianchu(self, month_zhi: str, day_zhi: str) -> str:
        """计算建除十二神"""
        month_idx = DI_ZHI.index(month_zhi)
        day_idx = DI_ZHI.index(day_zhi)
        offset = (day_idx - month_idx) % 12
        return JIANCHU[offset]

    def _calc_huangdao(self, day_zhi: str) -> tuple:
        """计算黄道黑道 (神名, 黄道/黑道)"""
        start_idx = HUANGDAO_START[day_zhi]
        # 从青龙开始，以日支为0偏移
        zhi_idx = DI_ZHI.index(day_zhi)
        offset = zhi_idx % 12
        shen_idx = (start_idx + offset) % 12
        return HUANGDAO_SHEN[shen_idx]

    def _calc_pengzu(self, day_gan: str, day_zhi: str) -> list:
        """获取彭祖百忌"""
        ji = []
        if day_gan in PENGZU_JI:
            ji.append(f"{day_gan}日{PENGZU_JI[day_gan]}")
        if day_zhi in PENGZU_JI:
            ji.append(f"{day_zhi}日{PENGZU_JI[day_zhi]}")
        return ji

    def _calc_general_yiji(self, jianchu: str, hd_type: str) -> tuple:
        """计算通用宜忌"""
        yi_set = set()
        ji_set = set()

        # 建除宜忌
        jc = JIANCHU_YIJI.get(jianchu, {})
        yi_set.update(jc.get("yi", []))
        ji_set.update(jc.get("ji", []))

        # 黄道黑道加成
        if hd_type == "黄道":
            yi_set.add("出行")
            yi_set.add("会友")
        else:
            ji_set.add("嫁娶")
            ji_set.add("开业")

        # 去重（宜和忌不应重叠）
        overlap = yi_set & ji_set
        yi_set -= overlap
        ji_set -= overlap

        return sorted(yi_set), sorted(ji_set)

    def _add_personal_analysis(self, result: YijiResult, user_bazi):
        """添加基于用户八字的个人分析"""
        rizhu = user_bazi.rizhu
        rizhu_wx = user_bazi.rizhu_wuxing
        day_gan = result.day_gan
        day_zhi = result.day_zhi

        parts = []

        # 日干 vs 日主（天干合/冲/生克）
        from .data.ganzhi import get_shishen, GAN_HE
        shishen = get_shishen(rizhu, day_gan)
        parts.append(f"今日{day_gan}日，对日主{rizhu}为{shishen}。")

        # 喜用神分析（简化版：五行平衡判断）
        scores = user_bazi.wuxing_scores
        weak_wx = min(scores, key=scores.get)
        strong_wx = max(scores, key=scores.get)

        day_gan_wx = GAN_WUXING[day_gan]
        day_zhi_wx = ZHI_WUXING[day_zhi]

        if day_gan_wx == weak_wx or day_zhi_wx == weak_wx:
            parts.append(f"今日{day_gan_wx}气旺，恰好补益你最弱的{weak_wx}，"
                        f"传统命理认为此日对你有益。")
            result.personal_yi.append("学习进修")
            result.personal_yi.append("重要会面")
        elif day_gan_wx == strong_wx:
            parts.append(f"今日{day_gan_wx}气与你的过旺五行相同，"
                        f"宜静不宜动，避免冲动决策。")
            result.personal_ji.append("冲动消费")
            result.personal_ji.append("重大决策")

        # 地支冲合分析
        user_day_zhi = user_bazi.day.zhi
        if ZHI_CHONG.get(day_zhi) == user_day_zhi:
            parts.append(f"今日{day_zhi}与你日支{user_day_zhi}相冲，"
                        f"古籍认为日支逢冲，不宜远行和重大决策。")
            result.personal_ji.append("远行")
            result.personal_ji.append("签约")
        elif ZHI_HE.get((day_zhi, user_day_zhi)):
            parts.append(f"今日{day_zhi}与你日支{user_day_zhi}相合，"
                        f"传统上认为利于合作与社交。")
            result.personal_yi.append("社交")
            result.personal_yi.append("合作洽谈")

        result.personal_analysis = " ".join(parts)


def get_today_yiji(user_bazi=None) -> YijiResult:
    """获取今日宜忌的便捷函数"""
    now = datetime.now()
    solar = Solar.fromYmdHms(now.year, now.month, now.day, 12, 0, 0)
    yj = DailyYiji()
    return yj.analyze(solar, user_bazi)
