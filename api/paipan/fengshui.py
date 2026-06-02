"""
阳宅风水分析引擎
================
基于《协纪辨方书》《阳宅十书》等古籍的阳宅风水判断。

用户输入房屋信息（门向/格局/缺角等），系统给出古典风水建议。
不涉及恐吓、不承诺改运，只提供传统文化参考。

用法:
  from api.paipan.fengshui import FengshuiEngine
  engine = FengshuiEngine()
  result = engine.analyze(house_info)
"""

from dataclasses import dataclass, field

# ===== 八宅风水基础数据 =====

# 八卦方位
BAGUA_DIRECTIONS = {
    "北": {"gua": "坎", "wuxing": "水", "num": 1},
    "西南": {"gua": "坤", "wuxing": "土", "num": 2},
    "东": {"gua": "震", "wuxing": "木", "num": 3},
    "东南": {"gua": "巽", "wuxing": "木", "num": 4},
    "西北": {"gua": "乾", "wuxing": "金", "num": 6},
    "西": {"gua": "兑", "wuxing": "金", "num": 7},
    "东北": {"gua": "艮", "wuxing": "土", "num": 8},
    "南": {"gua": "离", "wuxing": "火", "num": 9},
}

# 东四命/西四命（由出生年计算命卦）
DONGSI_GUA = {"坎", "离", "震", "巽"}  # 东四命
XISI_GUA = {"乾", "坤", "艮", "兑"}    # 西四命

# 九宫飞星2026年（丙午年）布局
# 流年飞星从中央开始：二黑→三碧→四绿→五黄→六白→七赤→八白→九紫→一白
JIUGONG_2026 = {
    "中宫": {"star": "二黑", "wuxing": "土", "ji_xiong": "凶"},
    "西北": {"star": "三碧", "wuxing": "木", "ji_xiong": "小凶"},
    "西":   {"star": "四绿", "wuxing": "木", "ji_xiong": "小吉"},
    "东北": {"star": "五黄", "wuxing": "土", "ji_xiong": "大凶"},
    "南":   {"star": "六白", "wuxing": "金", "ji_xiong": "吉"},
    "北":   {"star": "七赤", "wuxing": "金", "ji_xiong": "小凶"},
    "西南": {"star": "八白", "wuxing": "土", "ji_xiong": "大吉"},
    "东":   {"star": "九紫", "wuxing": "火", "ji_xiong": "大吉"},
    "东南": {"star": "一白", "wuxing": "水", "ji_xiong": "大吉"},
}

# 各功能区的理想方位
ROOM_IDEAL = {
    "大门": ["南", "东南", "东"],
    "主卧": ["西南", "西北", "东北"],
    "厨房": ["东", "东南"],
    "卫生间": ["北", "东北", "西"],
    "客厅": ["南", "东南", "西南"],
    "书房": ["北", "东北", "西北"],
}

# 形煞知识库
XINGSHA_KB = {
    "路冲": {"desc": "大门正对直路或走廊", "impact": "气场直冲，不利健康", "fix": "门前设屏风/玄关，或挂八卦镜"},
    "尖角煞": {"desc": "窗外有尖角建筑或物体正对", "impact": "尖角属火，易引发口舌是非", "fix": "窗台放阔叶植物遮挡"},
    "反弓煞": {"desc": "房屋位于道路弯道外侧", "impact": "气场反弓，不利财运", "fix": "门前设泰山石敢当或高墙"},
    "天斩煞": {"desc": "两栋高楼之间的缝隙正对窗户", "impact": "风口效应，气场急流", "fix": "挂厚重窗帘或摆放屏风"},
    "穿堂煞": {"desc": "大门直通后门/阳台，一通到底", "impact": "财气直进直出，不聚财", "fix": "中间设隔断/柜子/屏风阻挡"},
    "门对门": {"desc": "卧室门正对卫生间门或厨房门", "impact": "气场相冲，影响健康和睡眠", "fix": "常关门或挂门帘遮挡"},
}

# 缺角影响
QUEJIAO_IMPACT = {
    "西北": {"area": "男主人/事业", "fix": "西北角放金属摆件或白色装饰"},
    "西南": {"area": "女主人/婚姻", "fix": "西南角放陶瓷或黄色装饰"},
    "东":   {"area": "长子/健康", "fix": "东角放绿色植物或木制家具"},
    "东南": {"area": "长女/财运", "fix": "东南角放水景或绿色植物"},
    "北":   {"area": "次子/智慧", "fix": "北角放鱼缸或黑色装饰"},
    "南":   {"area": "次女/名声", "fix": "南角放红色装饰或灯具"},
    "东北": {"area": "幼子/学业", "fix": "东北角放山石或黄色装饰"},
    "西":   {"area": "幼女/口才", "fix": "西角放金属风铃或白色装饰"},
}


@dataclass
class FengshuiReport:
    """风水分析报告"""
    # 八宅分析
    house_gua: str = ""
    house_type: str = ""  # 东四宅/西四宅
    four_ji: list = field(default_factory=list)
    four_xiong: list = field(default_factory=list)

    # 九宫飞星
    jiugong_warnings: list = field(default_factory=list)

    # 功能区建议
    room_advice: list = field(default_factory=list)

    # 形煞
    xingsha_advice: list = field(default_factory=list)

    # 缺角
    quejiao_advice: list = field(default_factory=list)

    # 总体建议
    summary: str = ""


class FengshuiEngine:
    """阳宅风水分析引擎"""

    def analyze(self, house: dict) -> FengshuiReport:
        """
        分析阳宅风水。

        house参数:
          door_direction: 大门朝向（北/东北/东/东南/南/西南/西/西北）
          kitchen: 厨房位置
          bedroom: 主卧位置
          bathroom: 卫生间位置
          missing_corners: 缺角列表 ["西北","东南"]
          xingsha: 观察到的形煞 ["路冲","穿堂煞"]
          living_room: 客厅位置
          year: 出生年份（用于八宅命卦）
        """
        report = FengshuiReport()

        door = house.get("door_direction", "")
        if door and door in BAGUA_DIRECTIONS:
            # 1. 八宅分析
            self._analyze_bazhai(report, door)

            # 3. 九宫飞星
            self._analyze_jiugong(report)

            # 4. 功能区建议
            self._analyze_rooms(report, house)

        # 5. 形煞
        xingsha_list = house.get("xingsha", [])
        if xingsha_list:
            self._analyze_xingsha(report, xingsha_list)

        # 6. 缺角
        missing = house.get("missing_corners", [])
        if missing:
            self._analyze_quejiao(report, missing)

        # 7. 总体建议
        report.summary = self._generate_summary(report)

        return report

    def _analyze_bazhai(self, report: FengshuiReport, door: str):
        """八宅分析：根据大门朝向判断宅卦和四吉四凶方"""
        gua = BAGUA_DIRECTIONS[door]["gua"]
        report.house_gua = gua
        report.house_type = "东四宅" if gua in DONGSI_GUA else "西四宅"

        # 四吉四凶方位（简化版，以宅卦定）
        # 贪狼生气/巨门天医/武曲延年/辅弼伏位为吉
        # 禄存祸害/文曲六煞/破军绝命/廉贞五鬼为凶
        JI_XIONG_MAP = {
            "坎": {"生气":"东南","天医":"东","延年":"南","伏位":"北",
                   "祸害":"西","六煞":"西北","绝命":"西南","五鬼":"东北"},
            "离": {"生气":"东","天医":"东南","延年":"北","伏位":"南",
                   "祸害":"东北","六煞":"西南","绝命":"西北","五鬼":"西"},
            "震": {"生气":"南","天医":"北","延年":"东南","伏位":"东",
                   "祸害":"西南","六煞":"东北","绝命":"西","五鬼":"西北"},
            "巽": {"生气":"北","天医":"南","延年":"东","伏位":"东南",
                   "祸害":"西北","六煞":"西","绝命":"东北","五鬼":"西南"},
            "乾": {"生气":"西","天医":"东北","延年":"西南","伏位":"西北",
                   "祸害":"东南","六煞":"北","绝命":"南","五鬼":"东"},
            "坤": {"生气":"东北","天医":"西","延年":"西北","伏位":"西南",
                   "祸害":"东","六煞":"南","绝命":"北","五鬼":"东南"},
            "艮": {"生气":"西南","天医":"西北","延年":"西","伏位":"东北",
                   "祸害":"南","六煞":"东","绝命":"东南","五鬼":"北"},
            "兑": {"生气":"西北","天医":"西南","延年":"东北","伏位":"西",
                   "祸害":"北","六煞":"东南","绝命":"东","五鬼":"南"},
        }

        m = JI_XIONG_MAP.get(gua, {})
        report.four_ji = [f"{name}方({dir})" for name, dir in [
            ("生气", m.get("生气")), ("天医", m.get("天医")),
            ("延年", m.get("延年")), ("伏位", m.get("伏位"))] if dir]
        report.four_xiong = [f"{name}方({dir})" for name, dir in [
            ("绝命", m.get("绝命")), ("五鬼", m.get("五鬼")),
            ("祸害", m.get("祸害")), ("六煞", m.get("六煞"))] if dir]

    def _analyze_jiugong(self, report: FengshuiReport):
        """九宫飞星分析"""
        for pos, info in JIUGONG_2026.items():
            if info["ji_xiong"] in ("大凶", "凶"):
                report.jiugong_warnings.append(
                    f"{pos}方：{info['star']}星({info['wuxing']}，{info['ji_xiong']})，"
                    f"宜静不宜动，避免在此方位装修或动土"
                )
            elif info["ji_xiong"] == "大吉":
                report.jiugong_warnings.append(
                    f"{pos}方：{info['star']}星({info['wuxing']}，{info['ji_xiong']})，"
                    f"宜开门窗纳气，适合在此方位活动"
                )

    def _analyze_rooms(self, report: FengshuiReport, house: dict):
        """功能区布局建议"""
        for room, ideal_dirs in ROOM_IDEAL.items():
            actual = house.get(room.lower().replace(" ", "_"), "")
            if actual and actual not in ideal_dirs:
                report.room_advice.append(
                    f"{room}当前在{actual}方，理想方位是{'/'.join(ideal_dirs)}。"
                    f"若无法改动，可用五行化解。"
                )

    def _analyze_xingsha(self, report: FengshuiReport, xingsha_list: list):
        """形煞分析"""
        for xs in xingsha_list:
            if xs in XINGSHA_KB:
                info = XINGSHA_KB[xs]
                report.xingsha_advice.append(
                    f"{xs}：{info['desc']}。影响：{info['impact']}。化解：{info['fix']}。"
                )

    def _analyze_quejiao(self, report: FengshuiReport, missing: list):
        """缺角分析"""
        for corner in missing:
            if corner in QUEJIAO_IMPACT:
                info = QUEJIAO_IMPACT[corner]
                report.quejiao_advice.append(
                    f"{corner}角缺失：影响{info['area']}。{info['fix']}。"
                )

    def _generate_summary(self, report: FengshuiReport) -> str:
        """生成综合建议"""
        parts = []
        if report.house_gua:
            parts.append(f"此宅为{report.house_gua}宅（{report.house_type}）。"
                        f"吉方：{'、'.join(report.four_ji[:3])}。")
        if report.jiugong_warnings:
            parts.append(f"2026年流年飞星注意{len(report.jiugong_warnings)}处。")
        if report.room_advice:
            parts.append(f"功能区有{len(report.room_advice)}处可优化。")
        if report.xingsha_advice:
            parts.append(f"发现{len(report.xingsha_advice)}处形煞。")
        if report.quejiao_advice:
            parts.append(f"存在{len(report.quejiao_advice)}处缺角。")

        if not parts:
            parts.append("请补充房屋信息以获取详细分析。")

        return "".join(parts)
