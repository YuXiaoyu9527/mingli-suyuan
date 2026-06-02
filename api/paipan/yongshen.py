"""
用神推断引擎
============
自动判断扶抑用神、调候用神、通关用神。

核心逻辑参考《滴天髓阐微》《穷通宝鉴》。

用法:
  from api.paipan.yongshen import YongshenEngine
  engine = YongshenEngine()
  result = engine.analyze(bazi)
"""

from dataclasses import dataclass, field
from .data.ganzhi import TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING


@dataclass
class YongshenResult:
    """用神分析结果"""
    rizhu: str
    rizhu_wuxing: str
    wangshuai: str             # 旺衰判断: "身旺"/"身弱"/"中和"
    wangshuai_reason: str      # 旺衰原因

    fuyi_yongshen: list = field(default_factory=list)    # 扶抑用神
    tiaohou_yongshen: list = field(default_factory=list)  # 调候用神
    tongguan_yongshen: list = field(default_factory=list) # 通关用神
    recommended: list = field(default_factory=list)       # 综合推荐用神
    jishen: list = field(default_factory=list)            # 忌神

    analysis: str = ""          # 综合分析


class YongshenEngine:
    """用神推断引擎"""

    # 调候参考表（简化版，基于《穷通宝鉴》核心思想）
    # 日主天干 → 月支 → 调候用神
    TIAOHOU = {
        "甲": {"寅": "火", "卯": "火", "辰": "火", "巳": "水", "午": "水",
               "未": "水", "申": "火", "酉": "火", "戌": "火", "亥": "火",
               "子": "火", "丑": "火"},
        "乙": {"寅": "火", "卯": "火", "辰": "火", "巳": "水", "午": "水",
               "未": "水", "申": "火", "酉": "火", "戌": "火", "亥": "火",
               "子": "火", "丑": "火"},
        "丙": {"寅": "水", "卯": "水", "辰": "水", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "丁": {"寅": "水", "卯": "水", "辰": "水", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "戊": {"寅": "水", "卯": "水", "辰": "水", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "己": {"寅": "水", "卯": "水", "辰": "水", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "庚": {"寅": "土", "卯": "土", "辰": "火", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "辛": {"寅": "土", "卯": "土", "辰": "火", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "壬": {"寅": "土", "卯": "土", "辰": "土", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
        "癸": {"寅": "土", "卯": "土", "辰": "土", "巳": "水", "午": "水",
               "未": "水", "申": "水", "酉": "水", "戌": "水", "亥": "火",
               "子": "火", "丑": "火"},
    }

    # 五行生克关系
    WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    def analyze(self, bazi) -> YongshenResult:
        """推断用神"""
        rizhu = bazi.rizhu
        rizhu_wx = bazi.rizhu_wuxing
        month_zhi = bazi.month.zhi
        scores = bazi.wuxing_scores

        # 1. 旺衰判断
        wangshuai, ws_reason = self._judge_wangshuai(bazi, scores)

        # 2. 扶抑用神
        fuyi = self._calc_fuyi(rizhu_wx, wangshuai, scores)

        # 3. 调候用神
        tiaohou = self._calc_tiaohou(rizhu, month_zhi, rizhu_wx)

        # 4. 通关用神
        tongguan = self._calc_tongguan(bazi)

        # 5. 综合推荐
        recommended, jishen = self._recommend(fuyi, tiaohou, tongguan, rizhu_wx, wangshuai)

        # 6. 生成分析
        analysis = self._generate_analysis(rizhu, rizhu_wx, wangshuai, ws_reason,
                                           recommended, jishen, tiaohou)

        return YongshenResult(
            rizhu=rizhu,
            rizhu_wuxing=rizhu_wx,
            wangshuai=wangshuai,
            wangshuai_reason=ws_reason,
            fuyi_yongshen=fuyi,
            tiaohou_yongshen=tiaohou,
            tongguan_yongshen=tongguan,
            recommended=recommended,
            jishen=jishen,
            analysis=analysis,
        )

    def _judge_wangshuai(self, bazi, scores: dict) -> tuple:
        """判断日主旺衰"""
        rizhu_wx = bazi.rizhu_wuxing
        self_score = scores.get(rizhu_wx, 0)

        # 生我者为印（增加旺度）
        for wx_sheng, wx_bei_sheng in self.WUXING_SHENG.items():
            if wx_bei_sheng == rizhu_wx:
                self_score += scores.get(wx_sheng, 0) * 0.5  # 生我的算一半分
                break

        # 月令加成
        month_zhi = bazi.month.zhi
        month_wx = ZHI_WUXING[month_zhi]
        if month_wx == rizhu_wx:
            self_score += 10  # 月令同五行, 加10分
        for wx_sheng, wx_bei_sheng in self.WUXING_SHENG.items():
            if wx_bei_sheng == rizhu_wx and month_wx == wx_sheng:
                self_score += 8  # 月令生我, 加8分

        # 得地：日支是否同五行
        if ZHI_WUXING[bazi.day.zhi] == rizhu_wx:
            self_score += 5

        total = sum(scores.values())
        avg = total / 5 if total > 0 else 0

        if self_score > avg * 1.4:
            return "身旺", f"日主{rizhu_wx}得月令生扶，五行分数{self_score:.0f}高于均值{avg:.0f}"
        elif self_score < avg * 0.6:
            return "身弱", f"日主{rizhu_wx}失令，五行分数{self_score:.0f}低于均值{avg:.0f}"
        else:
            return "中和", f"日主{rizhu_wx}五行分数{self_score:.0f}接近均值{avg:.0f}"

    def _calc_fuyi(self, rizhu_wx: str, wangshuai: str, scores: dict) -> list:
        """计算扶抑用神"""
        if wangshuai == "身旺":
            # 身旺需要克/泄/耗
            yong = []
            # 克我者（官杀）
            for wx_ke, wx_bei_ke in self.WUXING_KE.items():
                if wx_bei_ke == rizhu_wx:
                    yong.append(wx_ke)
                    break
            # 我生者（食伤）
            yong.append(self.WUXING_SHENG.get(rizhu_wx, ""))
            # 我克者（财）— 排在最后
            for wx_k, wx_bk in self.WUXING_KE.items():
                if wx_k == rizhu_wx:
                    yong.append(wx_bk)
                    break
            return [y for y in yong if y]

        elif wangshuai == "身弱":
            # 身弱需要生/扶
            yong = [rizhu_wx]  # 比劫（同五行）
            for wx_s, wx_bs in self.WUXING_SHENG.items():
                if wx_bs == rizhu_wx:
                    yong.append(wx_s)  # 印（生我者）
                    break
            return yong

        return []

    def _calc_tiaohou(self, rizhu: str, month_zhi: str, rizhu_wx: str) -> list:
        """计算调候用神"""
        tiaohou = self.TIAOHOU.get(rizhu, {}).get(month_zhi, "")
        if tiaohou and tiaohou != rizhu_wx:
            return [tiaohou]
        return []

    def _calc_tongguan(self, bazi) -> list:
        """计算通关用神：看日主和最强的克星之间能否调和"""
        rizhu_wx = bazi.rizhu_wuxing
        scores = bazi.wuxing_scores

        # 找克日主的最强五行
        ke_rizhu_wx = None
        for k, v in self.WUXING_KE.items():
            if v == rizhu_wx:
                ke_rizhu_wx = k
                break

        if ke_rizhu_wx and scores.get(ke_rizhu_wx, 0) > scores.get(rizhu_wx, 0) * 1.2:
            # 克星太旺，需要通关
            # 通关 = 克星所生的五行（泄克星之气）
            tongguan = self.WUXING_SHENG.get(ke_rizhu_wx, "")
            if tongguan and tongguan != rizhu_wx:
                return [tongguan]

        return []

    def _recommend(self, fuyi: list, tiaohou: list, tongguan: list, rizhu_wx: str, wangshuai: str) -> tuple:
        """综合推荐用神和忌神"""
        recommended = []
        # 调候优先
        for wx in tiaohou:
            if wx not in recommended:
                recommended.append(wx)
        # 扶抑次之
        for wx in fuyi:
            if wx not in recommended:
                recommended.append(wx)
        # 通关补充
        for wx in tongguan:
            if wx not in recommended:
                recommended.append(wx)

        # 忌神 = 克用神的五行 + 用神所克的五行
        jishen = set()
        for yong in recommended:
            for k, v in self.WUXING_KE.items():
                if v == yong:
                    jishen.add(k)
                if k == yong:
                    jishen.add(v)

        # 去掉重复的用神
        jishen.discard(rizhu_wx)  # 日主本身不是忌神
        for yong in recommended:
            jishen.discard(yong)

        return recommended[:3], sorted(jishen)[:3]

    def _generate_analysis(self, rizhu, rizhu_wx, wangshuai, ws_reason, recommended, jishen, tiaohou) -> str:
        """生成综合分析文本"""
        parts = [
            f"日主{rizhu}（{rizhu_wx}），{wangshuai}。{ws_reason}。"
        ]

        if recommended:
            wx_names = {"木":"木（青/东/春/肝）","火":"火（红/南/夏/心）",
                        "土":"土（黄/中/长夏/脾）","金":"金（白/西/秋/肺）",
                        "水":"水（黑/北/冬/肾）"}
            rec_str = "、".join(wx_names.get(w, w) for w in recommended)
            parts.append(f"综合推荐用神：{rec_str}。")

        if jishen:
            ji_str = "、".join(jishen)
            parts.append(f"忌神：{ji_str}。")

        if tiaohou:
            parts.append(f"调候用神为{tiaohou[0]}，建议在生活中多接触{tiaohou[0]}行相关的事物。")

        if wangshuai == "身旺":
            parts.append("身旺宜克泄耗，适合从事挑战性强、需要输出的工作。")
        elif wangshuai == "身弱":
            parts.append("身弱宜生扶，适合在稳定环境中积累成长。")

        return "".join(parts)
