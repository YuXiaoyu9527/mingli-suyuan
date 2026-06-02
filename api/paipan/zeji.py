"""
择吉搜索引擎
============
输入活动类型（结婚/搬家/开业等），返回未来合适的吉日。

基于《协纪辨方书》规则 + lunar_python 每日宜忌数据。

用法:
  from api.paipan.zeji import ZejiEngine
  engine = ZejiEngine()
  dates = engine.search("结婚", days=90)
"""

from datetime import datetime, timedelta
from lunar_python import Solar


# 活动关键词映射（用于匹配 lunar_python 返回的宜忌词条）
ACTIVITY_KEYWORDS = {
    "结婚": ["嫁娶", "纳采", "订盟", "订婚"],
    "搬家": ["移徙", "入宅", "搬家"],
    "开业": ["开市", "开业", "交易", "立券"],
    "出行": ["出行", "远行", "旅游"],
    "动土": ["动土", "修造", "起基"],
    "安葬": ["安葬", "下葬"],
    "签约": ["签约", "立券", "交易", "订盟"],
    "入学": ["入学", "习艺"],
    "求医": ["治病", "求医", "疗病"],
    "祭祀": ["祭祀", "祈福", "酬神"],
}


class ZejiEngine:
    """择吉搜索引擎"""

    def search(
        self,
        activity: str,
        days: int = 90,
        user_bazi=None,
    ) -> list[dict]:
        """
        搜索未来适合某项活动的吉日。

        Args:
            activity: 活动类型（结婚/搬家/开业/出行/动土/安葬/签约/入学/求医/祭祀）
            days: 搜索未来多少天
            user_bazi: 用户八字（可选，用于个人冲合过滤）

        Returns:
            按评分排序的吉日列表
        """
        # 1. 匹配关键词
        keywords = ACTIVITY_KEYWORDS.get(activity, [activity])

        # 2. 扫描日期
        today = datetime.now()
        results = []

        for offset in range(days):
            date = today + timedelta(days=offset)
            solar = Solar.fromYmdHms(date.year, date.month, date.day, 12, 0, 0)
            lunar = solar.getLunar()

            day_yi = [y for y in lunar.getDayYi() if y] or []
            day_ji = [j for j in lunar.getDayJi() if j] or []

            # 检查是否在宜中
            yi_match = any(kw in yi for kw in keywords for yi in day_yi)
            ji_match = any(kw in ji for kw in keywords for ji in day_ji)

            # 宜中且不在忌中
            if yi_match and not ji_match:
                score = self._score_day(lunar)
                results.append({
                    "date": f"{date.year}-{date.month:02d}-{date.day:02d}",
                    "lunar": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                    "day_ganzhi": lunar.getDayInGanZhi(),
                    "jianchu": lunar.getZhiXing(),
                    "tianshen": lunar.getDayTianShen(),
                    "tianshen_type": lunar.getDayTianShenType(),
                    "tianshen_luck": lunar.getDayTianShenLuck(),
                    "jishen": lunar.getDayJiShen(),
                    "yi": day_yi[:5],
                    "ji": day_ji[:5],
                    "score": score,
                    "week": f"星期{lunar.getWeekInChinese()}",
                })

        # 3. 按评分排序，取前20
        results.sort(key=lambda x: -x["score"])
        return results[:20]

    def _score_day(self, lunar) -> int:
        """给某日打分"""
        score = 0

        # 黄道+10
        if lunar.getDayTianShenType() == "黄道":
            score += 10
            if lunar.getDayTianShenLuck() == "吉":
                score += 5
        else:
            score -= 5

        # 建除吉日+8
        jianchu = lunar.getZhiXing()
        if jianchu in ("成", "开"):
            score += 8
        elif jianchu in ("建", "满", "平", "定", "收"):
            score += 3
        elif jianchu in ("破", "闭"):
            score -= 10
            return max(0, score)  # 破日闭日直接最低分

        # 天德月德+15
        jishen = lunar.getDayJiShen()
        for js in jishen:
            if "天德" in js or "月德" in js:
                score += 15
                break

        # 吉神数量加分
        score += min(10, len(jishen) * 2)

        # 凶煞扣分
        xiongsha = lunar.getDayXiongSha()
        score -= min(10, len(xiongsha) * 2)

        return max(0, score)

    def search_with_personal(self, activity: str, bazi, days: int = 90) -> list[dict]:
        """搜索吉日并叠加个人八字分析"""
        results = self.search(activity, days)

        for r in results:
            # 检查冲生肖
            day_zhi = r["day_ganzhi"][1]
            user_zhi = bazi.year.zhi
            if day_zhi == user_zhi:
                r["personal_warning"] = f"此日冲你的生肖"
                r["score"] -= 10
            # 检查冲日支
            if day_zhi == bazi.day.zhi:
                r["personal_warning"] = f"此日冲你的日支"
                r["score"] -= 15

        results.sort(key=lambda x: -x["score"])
        return results
