"""
每日开运建议引擎
================
根据当日干支+用户八字用神，给出穿着/行动/搭配建议。

规则基于五行生克，零AI。

用法:
  from api.paipan.daily_tips import DailyTips
  tips = DailyTips().generate(day_ganzhi, user_yongshen)
"""

from dataclasses import dataclass, field

# ===== 五行 → 颜色/材质/方位 =====
WUXING_STYLE = {
    "木": {
        "colors": ["绿色", "青色", "翠绿", "墨绿"],
        "materials": ["木质饰品", "绿松石", "翡翠"],
        "direction": "东方",
        "emoji": "🌿",
    },
    "火": {
        "colors": ["红色", "紫色", "橙色", "玫红"],
        "materials": ["红玛瑙", "紫水晶", "红绳"],
        "direction": "南方",
        "emoji": "🔥",
    },
    "土": {
        "colors": ["黄色", "棕色", "卡其色", "米色"],
        "materials": ["黄水晶", "陶瓷", "玉石"],
        "direction": "中央",
        "emoji": "🏔️",
    },
    "金": {
        "colors": ["白色", "金色", "银色", "浅灰"],
        "materials": ["金属饰品", "白水晶", "银饰"],
        "direction": "西方",
        "emoji": "✨",
    },
    "水": {
        "colors": ["黑色", "深蓝", "藏青", "灰色"],
        "materials": ["黑曜石", "海蓝宝", "珍珠"],
        "direction": "北方",
        "emoji": "💧",
    },
}

# ===== 五行 → 宜做的事 =====
WUXING_ACTIVITY = {
    "木": ["早起晨跑", "读书学习", "制定计划", "养绿植", "写作", "学新技能"],
    "火": ["运动健身", "社交聚会", "演讲表达", "创意头脑风暴", "面试", "发布作品"],
    "土": ["整理收纳", "理财规划", "园艺", "慈善捐款", "团队协作", "签订合同"],
    "金": ["断舍离", "做决策", "精进技艺", "谈判", "处理文书", "清理杂物"],
    "水": ["冥想静坐", "深度思考", "休息放松", "听音乐", "泡澡", "复盘反思"],
}

# ===== 五行 → 忌做的事 =====
WUXING_AVOID = {
    "木": ["熬夜晚睡", "冲动消费", "暴饮暴食"],
    "火": ["与人争执", "过度劳累", "高风险投资"],
    "土": ["懒散拖延", "封闭自己", "重大变动"],
    "金": ["犹豫不决", "感情用事", "过度消费"],
    "水": ["胡思乱想", "孤僻自闭", "冒险行为"],
}


@dataclass
class DailyTips:
    """每日建议"""

    # 穿着
    wear_colors: list = field(default_factory=list)
    wear_detail: str = ""

    # 配饰
    accessory: list = field(default_factory=list)

    # 宜做
    suggest_do: list = field(default_factory=list)

    # 忌做
    suggest_avoid: list = field(default_factory=list)

    # 方位
    lucky_direction: str = ""

    # 综合文案
    daily_quote: str = ""


def generate(day_ganzhi: str, recommended_wuxing: list, jishen: list, day_gan: str = "", day_zhi: str = "") -> DailyTips:
    """
    生成每日开运建议。

    Args:
        day_ganzhi: 今日干支 (如"丙午")
        recommended_wuxing: 用户用神（推荐五行列表）
        jishen: 用户忌神五行列表
        day_gan: 日干
        day_zhi: 日支
    """
    tips = DailyTips()

    if not recommended_wuxing:
        tips.daily_quote = "填写出生日期，获取专属每日开运建议。"
        return tips

    # 1. 穿什么：用神对应的颜色
    primary_wx = recommended_wuxing[0]  # 第一用神
    secondary_wx = recommended_wuxing[1] if len(recommended_wuxing) > 1 else None

    style = WUXING_STYLE.get(primary_wx, {})
    tips.wear_colors = style.get("colors", ["白色"])[:3]
    tips.accessory = style.get("materials", ["金属饰品"])[:2]

    if secondary_wx and secondary_wx in WUXING_STYLE:
        tips.wear_colors.append(WUXING_STYLE[secondary_wx]["colors"][0])

    emoji = style.get("emoji", "✨")
    tips.wear_detail = (
        f"今日宜{primary_wx}行，建议穿{'、'.join(tips.wear_colors)}色系服饰。"
        f"{emoji} 主色调：{tips.wear_colors[0]}。"
        f"配饰可选{'、'.join(tips.accessory)}。"
    )

    # 2. 做什么：用神对应的活动
    if primary_wx in WUXING_ACTIVITY:
        tips.suggest_do = WUXING_ACTIVITY[primary_wx][:4]

    # 3. 忌做什么：忌神对应的活动
    for js in jishen[:2]:
        if js in WUXING_AVOID:
            tips.suggest_avoid.extend(WUXING_AVOID[js][:2])
    tips.suggest_avoid = list(set(tips.suggest_avoid))[:4]
    if not tips.suggest_avoid:
        tips.suggest_avoid = ["过度劳累", "与人争执"]

    # 4. 方位
    tips.lucky_direction = style.get("direction", "")

    # 5. 综合文案
    color_str = tips.wear_colors[0] if tips.wear_colors else "白色"
    do_str = tips.suggest_do[0] if tips.suggest_do else "按部就班"
    tips.daily_quote = (
        f"今日宜着{color_str}，宜{do_str}。"
        f"旺{primary_wx}行之气，助你一天顺遂。"
    )

    return tips


def generate_from_bazi(day_ganzhi: str, yongshen_result, day_gan: str = "", day_zhi: str = "") -> DailyTips:
    """从用神分析结果生成建议"""
    return generate(
        day_ganzhi=day_ganzhi,
        recommended_wuxing=yongshen_result.recommended,
        jishen=yongshen_result.jishen,
        day_gan=day_gan,
        day_zhi=day_zhi,
    )
