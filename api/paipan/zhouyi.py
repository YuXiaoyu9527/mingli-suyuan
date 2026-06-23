"""
周易占卜引擎
============
六爻起卦 + 64卦解读 + 五行调和具体建议。

起卦方法：
- 随机起卦：随机生成六爻（每爻为阴/阳/变爻）
- 时间起卦（梅花易数）：以年月日时数字起卦，含体用生克
- 数字起卦：以用户提供的数字起卦

五行调和：基于卦象五行 + 体用生克，给出穿衣/配饰/方位/行为的
具体可操作建议，帮助用户"补不足、泄有余"。

用法:
  from api.paipan.zhouyi import ZhouyiEngine
  engine = ZhouyiEngine()
  result = engine.divine("我想问事业")
"""

import random
from dataclasses import dataclass, field

# 64卦简表（卦名+卦辞+核心含义）
GUACI = {
    "111111": {"name":"乾为天","meaning":"刚健中正，自强不息","advice":"宜积极进取，不宜消极等待","element":"金","direction":"西北"},
    "000000": {"name":"坤为地","meaning":"柔顺包容，厚德载物","advice":"宜顺势而为，不宜强行出头","element":"土","direction":"西南"},
    "010001": {"name":"水雷屯","meaning":"初生艰难，万事开头难","advice":"宜耐心筹划，不宜急躁冒进","element":"水","direction":"北"},
    "100010": {"name":"山水蒙","meaning":"蒙昧初开，需要启蒙","advice":"宜虚心求教，不宜自以为是","element":"土","direction":"东北"},
    "010111": {"name":"水天需","meaning":"等待时机，耐心守候","advice":"宜静待时机，不宜贸然行动","element":"水","direction":"北"},
    "111010": {"name":"天水讼","meaning":"争讼不和，需防口舌","advice":"宜退一步海阔天空，不宜争强好胜","element":"金","direction":"西北"},
    "000010": {"name":"地水师","meaning":"统兵出征，需有组织","advice":"宜团结协作，不宜单打独斗","element":"土","direction":"西南"},
    "010000": {"name":"水地比","meaning":"相亲相辅，团结和谐","advice":"宜广结善缘，不宜孤立自己","element":"水","direction":"北"},
    "110111": {"name":"风天小畜","meaning":"小有积蓄，尚待发展","advice":"宜积少成多，不宜贪大求快","element":"木","direction":"东南"},
    "111011": {"name":"天泽履","meaning":"如履薄冰，谨慎行事","advice":"宜谨言慎行，不宜鲁莽冲动","element":"金","direction":"西北"},
    "000111": {"name":"地天泰","meaning":"天地交泰，万事亨通","advice":"大吉之卦，宜把握时机","element":"土","direction":"西南"},
    "111000": {"name":"天地否","meaning":"天地不交，闭塞不通","advice":"宜修身养性，不宜强求突破","element":"金","direction":"西北"},
    "111101": {"name":"天火同人","meaning":"志同道合，与人协作","advice":"宜广交朋友，不宜独断专行","element":"金","direction":"西北"},
    "101111": {"name":"火天大有","meaning":"富有盛大，收获满满","advice":"宜分享成果，不宜独享其成","element":"火","direction":"南"},
    "000100": {"name":"地山谦","meaning":"谦虚谨慎，有而不居","advice":"宜保持谦虚，不宜骄傲自满","element":"土","direction":"西南"},
    "001000": {"name":"雷地豫","meaning":"愉悦安乐，顺时而动","advice":"宜顺势而为，不宜得意忘形","element":"木","direction":"东"},
    "011001": {"name":"泽雷随","meaning":"随顺变化，灵活应对","advice":"宜随机应变，不宜固执己见","element":"金","direction":"西"},
    "100110": {"name":"山风蛊","meaning":"积弊已久，需除旧布新","advice":"宜整顿改革，不宜因循守旧","element":"土","direction":"东北"},
    "000011": {"name":"地泽临","meaning":"君临天下，亲民治理","advice":"宜亲力亲为，不宜高高在上","element":"土","direction":"西南"},
    "110000": {"name":"风地观","meaning":"观察审视，洞察本质","advice":"宜深思熟虑，不宜急于下结论","element":"木","direction":"东南"},
    "101001": {"name":"火雷噬嗑","meaning":"咬合决断，清除障碍","advice":"宜果断决策，不宜犹豫不决","element":"火","direction":"南"},
    "100101": {"name":"山火贲","meaning":"修饰文饰，注重外表","advice":"宜内外兼修，不宜华而不实","element":"土","direction":"东北"},
    "100000": {"name":"山地剥","meaning":"剥落衰败，根基动摇","advice":"宜固本培元，不宜大动干戈","element":"土","direction":"东北"},
    "000001": {"name":"地雷复","meaning":"一阳来复，否极泰来","advice":"宜重新开始，不宜沉溺过往","element":"土","direction":"西南"},
    "111001": {"name":"天雷无妄","meaning":"不妄为，顺其自然","advice":"宜顺势而为，不宜投机取巧","element":"金","direction":"西北"},
    "100111": {"name":"山天大畜","meaning":"大有积蓄，厚积薄发","advice":"宜厚积薄发，不宜急于求成","element":"土","direction":"东北"},
    "100001": {"name":"山雷颐","meaning":"颐养天年，修身养性","advice":"宜养生保健，不宜透支体力","element":"土","direction":"东北"},
    "011110": {"name":"泽风大过","meaning":"大过其度，物极必反","advice":"宜及时调整，不宜一意孤行","element":"金","direction":"西"},
    "010010": {"name":"坎为水","meaning":"重重险阻，需谨慎应对","advice":"宜以柔克刚，不宜硬碰硬","element":"水","direction":"北"},
    "101101": {"name":"离为火","meaning":"光明依附，需有依托","advice":"宜坚守正道，不宜投机取巧","element":"火","direction":"南"},
    "011100": {"name":"泽山咸","meaning":"感应相通，心有灵犀","advice":"宜坦诚相待，不宜猜忌怀疑","element":"金","direction":"西"},
    "001110": {"name":"雷风恒","meaning":"恒久不变，持之以恒","advice":"宜坚持不懈，不宜半途而废","element":"木","direction":"东"},
    "111100": {"name":"天山遁","meaning":"退避隐忍，以退为进","advice":"宜暂时退让，不宜强出头","element":"金","direction":"西北"},
    "001111": {"name":"雷天大壮","meaning":"强盛壮大，势不可挡","advice":"宜乘势而上，但不可恃强凌弱","element":"木","direction":"东"},
    "101000": {"name":"火地晋","meaning":"晋升进步，蒸蒸日上","advice":"宜积极进取，不可贪功冒进","element":"火","direction":"南"},
    "000101": {"name":"地火明夷","meaning":"光明受损，韬光养晦","advice":"宜隐忍待时，不宜锋芒毕露","element":"土","direction":"西南"},
    "110101": {"name":"风火家人","meaning":"家庭和睦，各安其位","advice":"宜注重家庭，不宜忽略亲情","element":"木","direction":"东南"},
    "101011": {"name":"火泽睽","meaning":"乖离不合，求同存异","advice":"宜求同存异，不宜强求一致","element":"火","direction":"南"},
    "010100": {"name":"水山蹇","meaning":"艰难险阻，步履维艰","advice":"宜脚踏实地，不宜好高骛远","element":"水","direction":"北"},
    "001010": {"name":"雷水解","meaning":"困难解除，雨过天晴","advice":"宜乘势而为，不宜再陷困局","element":"木","direction":"东"},
    "110001": {"name":"山泽损","meaning":"损下益上，有失有得","advice":"宜懂得取舍，不宜斤斤计较","element":"土","direction":"东北"},
    "100011": {"name":"风雷益","meaning":"增益有利，见善则迁","advice":"宜乐于助人，不宜自私自利","element":"木","direction":"东南"},
    "011111": {"name":"泽天夬","meaning":"决断裁决，当断则断","advice":"宜果断决策，不宜拖泥带水","element":"金","direction":"西"},
    "111110": {"name":"天风姤","meaning":"不期而遇，邂逅相逢","advice":"宜把握机缘，不宜强求结果","element":"金","direction":"西北"},
    "000110": {"name":"地风升","meaning":"上升发展，步步高升","advice":"宜循序渐进，不宜一步登天","element":"土","direction":"西南"},
    "011000": {"name":"泽水困","meaning":"困顿窘迫，需守正待时","advice":"宜坚守正道，不宜铤而走险","element":"金","direction":"西"},
    "010110": {"name":"水风井","meaning":"井然有序，滋养万物","advice":"宜修身养性，不宜急于求成","element":"水","direction":"北"},
    "101110": {"name":"泽火革","meaning":"变革更新，除旧布新","advice":"宜顺势变革，不宜固步自封","element":"金","direction":"西"},
    "001101": {"name":"火风鼎","meaning":"鼎新革故，稳固发展","advice":"宜稳扎稳打，不宜冒进改革","element":"火","direction":"南"},
    "001001": {"name":"震为雷","meaning":"震动警醒，临危不乱","advice":"宜沉着应对，不宜惊慌失措","element":"木","direction":"东"},
    "100100": {"name":"艮为山","meaning":"止于当止，知止不殆","advice":"宜适可而止，不宜贪得无厌","element":"土","direction":"东北"},
    "110100": {"name":"风山渐","meaning":"循序渐进，逐步发展","advice":"宜稳步推进，不宜急于求成","element":"木","direction":"东南"},
    "001011": {"name":"雷泽归妹","meaning":"少女归嫁，婚姻大事","advice":"宜顺势而为，不宜强求撮合","element":"木","direction":"东"},
    "101100": {"name":"雷火丰","meaning":"丰盛盈满，日中则昃","advice":"宜居安思危，不宜骄傲自满","element":"木","direction":"东"},
    "001100": {"name":"火山旅","meaning":"旅居在外，漂泊不定","advice":"宜随遇而安，不宜固守不变","element":"火","direction":"南"},
    "110110": {"name":"巽为风","meaning":"柔顺谦逊，风行草偃","advice":"宜顺势而为，不宜强行改变","element":"木","direction":"东南"},
    "011011": {"name":"兑为泽","meaning":"喜悦和乐，沟通顺利","advice":"宜广泛交流，不宜孤芳自赏","element":"金","direction":"西"},
    "110010": {"name":"风水涣","meaning":"涣散分离，需凝聚人心","advice":"宜团结一致，不宜各自为政","element":"木","direction":"东南"},
    "010011": {"name":"水泽节","meaning":"节制有度，适可而止","advice":"宜量力而行，不宜铺张浪费","element":"水","direction":"北"},
    "110011": {"name":"风泽中孚","meaning":"诚信中正，以诚待人","advice":"宜以诚待人，不宜虚情假意","element":"木","direction":"东南"},
    "001100": {"name":"雷山小过","meaning":"小有过失，及时纠正","advice":"宜防微杜渐，不宜因小失大","element":"木","direction":"东"},
    "010101": {"name":"水火既济","meaning":"大功告成，守成不易","advice":"宜居安思危，不宜得意忘形","element":"水","direction":"北"},
    "101010": {"name":"火水未济","meaning":"未竟之业，仍需努力","advice":"宜继续努力，不宜半途而废","element":"火","direction":"南"},
}

# 五行调和知识库
WUXING_COLORS = {
    "金": ["白","银","浅灰","米白","香槟金"],
    "木": ["绿","青","翠绿","橄榄绿","浅蓝"],
    "水": ["黑","深蓝","藏青","深灰","蓝黑"],
    "火": ["红","紫","玫红","橙红","亮粉"],
    "土": ["黄","棕","卡其","米色","咖啡"],
}

WUXING_ITEMS = {
    "金": ["银色项链或耳钉","白色运动鞋","金属框眼镜","浅灰围巾","白色手表","圆形小镜子","不锈钢保温杯"],
    "木": ["绿色T恤或衬衫","木质手串","帆布包或棉麻围巾","绿色手机壳","绿植盆栽","竹制书签","棉麻帽子"],
    "水": ["黑色镜框或墨镜","深蓝色背包","黑色手表","深灰鸭舌帽","黑色水杯","深蓝色衬衫","黑色运动鞋"],
    "火": ["红色围巾或丝巾","红绳手链","红色棒球帽","玫红色唇膏","红色手机壳","暖光小夜灯","红色笔记本"],
    "土": ["棕色皮带或手表带","卡其色外套","米色运动鞋","棕色皮质钱包","陶瓷茶杯","帆布托特包","茶色太阳镜"],
}

WUXING_ACTIONS = {
    "金": ["整理桌面/断舍离","制定清晰的时间表","穿白色或银灰色衣服","在西北方位放置金属摆件","早上7-9点做重要决策"],
    "木": ["养一盆绿植","早起锻炼舒展身体","穿绿色或青色衣服","在东方位放一盆富贵竹","制定长期规划"],
    "水": ["多喝水/泡茶","冥想静坐10分钟","穿黑色或深蓝色衣服","在北方位放一杯水/鱼缸","重要洽谈安排在下午"],
    "火": ["点燃香薰蜡烛","穿红色或紫色衣服","在南方位放一盏暖灯","主动社交联系三人","重要电话在中午11-1点打"],
    "土": ["脚踏实地做好手头事","穿黄色或棕色衣服","在中宫位放一盆黄土/陶器","每工作45分钟休息5分钟","周末去公园踩踩泥土"],
}


@dataclass
class YaoLine:
    """一爻"""
    position: int      # 1-6（从下往上）
    type: str          # "阳" / "阴"
    is_changing: bool  # 是否变爻


@dataclass
class HexagramResult:
    """占卜结果"""
    question: str                  # 所求问题
    original_code: str             # 本卦二进制码
    original_name: str             # 本卦名
    original_meaning: str          # 本卦含义
    original_advice: str           # 本卦建议
    original_element: str          # 五行
    direction: str                 # 方位

    changing_lines: list = field(default_factory=list)  # 变爻位置
    changed_code: str = ""         # 变卦二进制码
    changed_name: str = ""         # 变卦名
    changed_meaning: str = ""      # 变卦含义

    analysis: str = ""             # 卦象解读
    suggestion: str = ""           # 综合建议
    wuxing_advice: dict = field(default_factory=dict)  # 五行调和具体举措


class ZhouyiEngine:
    """周易占卜引擎（整合梅花易数+五行调和）"""

    # 八卦对应（梅花易数先天八卦数）
    BAGUA_NUM = {1:("乾","天","☰"),2:("兑","泽","☱"),3:("离","火","☲"),
                 4:("震","雷","☳"),5:("巽","风","☴"),6:("坎","水","☵"),
                 7:("艮","山","☶"),8:("坤","地","☷")}

    # 八卦五行
    BAGUA_WUXING = {"乾":"金","兑":"金","离":"火","震":"木","巽":"木","坎":"水","艮":"土","坤":"土"}

    # 生克关系
    SHENG_KE = {
        ("木","火"):"生",("火","土"):"生",("土","金"):"生",("金","水"):"生",("水","木"):"生",
        ("木","土"):"克",("土","水"):"克",("水","火"):"克",("火","金"):"克",("金","木"):"克",
    }

    def divine(self, question: str) -> HexagramResult:
        """随机起卦占卜"""
        lines = []
        code_parts = []
        changing = []
        for i in range(6):
            r = random.randint(1, 4)
            if r == 1:  # 老阳（变爻）
                lines.append(YaoLine(position=i+1, type="阳", is_changing=True))
                code_parts.append("1")
                changing.append(i)
            elif r == 2:  # 少阳
                lines.append(YaoLine(position=i+1, type="阳", is_changing=False))
                code_parts.append("1")
            elif r == 3:  # 老阴（变爻）
                lines.append(YaoLine(position=i+1, type="阴", is_changing=True))
                code_parts.append("0")
                changing.append(i)
            else:  # 少阴
                lines.append(YaoLine(position=i+1, type="阴", is_changing=False))
                code_parts.append("0")

        original_code = "".join(code_parts)
        original = GUACI.get(original_code, {"name":"未识别的卦","meaning":"—","advice":"—","element":"—","direction":"—"})

        changed_parts = []
        for i, c in enumerate(code_parts):
            if i in changing:
                changed_parts.append("0" if c == "1" else "1")
            else:
                changed_parts.append(c)
        changed_code = "".join(changed_parts)
        changed = GUACI.get(changed_code, {})

        result = HexagramResult(
            question=question,
            original_code=original_code,
            original_name=original.get("name",""),
            original_meaning=original.get("meaning",""),
            original_advice=original.get("advice",""),
            original_element=original.get("element",""),
            direction=original.get("direction",""),
            changing_lines=changing,
            changed_code=changed_code,
            changed_name=changed.get("name","无变卦"),
            changed_meaning=changed.get("meaning",""),
        )

        result.analysis = self._analyze(result)
        result.suggestion = self._suggest(result)
        result.wuxing_advice = self._build_wuxing_advice(result)
        return result

    def _analyze(self, r: HexagramResult) -> str:
        """白话分析卦象"""
        parts = [f"你问「{r.question}」，占得{r.original_name}。\n"]
        parts.append(self._explain_hexagram(r.original_name))
        if r.changing_lines:
            yao_nums = "、".join(str(p+1) for p in r.changing_lines)
            parts.append(f"\n\n有变爻在第{yao_nums}爻，变为{r.changed_name}。")
            parts.append(self._explain_change(r.original_name, r.changed_name))
        return "".join(parts)

    def _suggest(self, r: HexagramResult) -> str:
        """白话建议——根据问题类型和卦象给出行动指南"""
        q = r.question
        hex_name = r.original_name
        has_change = len(r.changing_lines) > 0

        # 判断问题类型
        if any(w in q for w in ["工作","换工作","事业","创业","面试","升职","成单","客户","合同"]):
            topic = "事业"
        elif any(w in q for w in ["感情","恋爱","婚姻","结婚","分手","复合","对象","男朋友","女朋友"]):
            topic = "感情"
        elif any(w in q for w in ["财运","赚钱","投资","生意","钱","理财"]):
            topic = "财运"
        elif any(w in q for w in ["考试","学习","成绩","考试","考"]):
            topic = "学业"
        elif any(w in q for w in ["健康","身体","病","治疗"]):
            topic = "健康"
        else:
            topic = "综合"

        base = self._generate_advice(hex_name, topic, has_change)
        if has_change:
            base += "\n\n⚠️ 卦象有变爻，说明事情还在变化中——你现在做出的调整会直接影响最终走向。不要被动等待。"
        return base

    def _explain_hexagram(self, name: str) -> str:
        """64卦白话详解"""
        DETAILED_GUA = {
            "乾为天": "六条阳爻，纯阳之象。就像正午的太阳——光芒万丈，势不可挡。代表你正处于最强劲的状态，但也提醒：物极必反，刚极易折。保持谦虚比展示力量更重要。",
            "坤为地": "大地包容万物，不争不抢却能承载一切。这个卦告诉你：不要急于出人头地，做好手头的事，像大地一样稳。柔顺不是软弱，是另一种力量。",
            "水雷屯": "屯是万物初生——种子刚发芽，使尽了全身力气才冒出地面。你做的事正处于起步阶段，每一步都不容易。但这正常，每颗种子都要经历这一步。",
            "山水蒙": "蒙是蒙昧初开。就像一个刚上学的孩子，很多事还不懂。别装了，不懂就去问。找到好的老师或前辈，虚心请教，能少走很多弯路。",
            "水天需": "需就是等。不是消极的等，是像农民等庄稼成熟——你知道它会长出来，但不能拔苗助长。现在最好的行动就是不乱动，做好准备工作。",
            "天水讼": "讼是争辩、打官司。你现在可能正陷入一场争执。继续纠缠下去，双方都输。退一步不是认输，是止损。",
            "地水师": "师是军队。组织一群人做事，关键在纪律和公平。你现在管着一摊子事的话，记住：以身作则比发号施令有用。",
            "水地比": "比是亲近、团结。这个卦很好——说明有靠谱的人愿意帮你。别一个人扛，去找那个对的人合作。",
            "风天小畜": "小畜是小有积蓄。不算大富大贵，但已经在正轨上了。继续积累，不要急。积少成多比一夜暴富可靠。",
            "天泽履": "履是踩在薄冰上走路。你现在做的事有风险，每一步都要试探。小心不是胆小，是对自己负责。",
            "地天泰": "天地交泰——六十四卦里最好的卦之一。上通下达，事事顺畅。但好卦也有提醒：顺境最容易让人松懈。保持清醒，好运会持续。",
            "天地否": "否是不通、闭塞。上下不沟通，左右不配合。你感觉自己被困住了。先别想着突围——看看是不是自己关上了某扇门。打开沟通渠道是第一要务。",
            "天火同人": "同人是志同道合。你会在人群中找到一个对的人——合作伙伴、伴侣。走出去，不要待在家里等。",
            "火天大有": "这是丰收的卦。你之前种下的努力，现在该收获了。但丰收之后怎么分配，决定了你能不能守住。",
            "地山谦": "谦卦六爻全吉——周易里唯一一个。谦虚不是装，是真正认识到自己还有不足。这个状态本身就是最好的护身符。",
            "雷地豫": "豫是愉悦安乐。顺风顺水的时候到了。享受它，但别过头——乐极生悲不是开玩笑的。",
            "泽雷随": "随是随顺变化。风向变了，你就转舵。不固执，不纠结。灵活比坚持更聪明。",
            "山风蛊": "蛊是器皿里长了虫子——事情已经烂了一段时间。不是修修补补的时候，要大扫除。该断的关系、该改的习惯，一次性处理。",
            "地泽临": "临是俯身看。居高临下地审视自己的处境。你离目标很近，但还需要最后一推。",
            "风地观": "观是观察、审视。先别行动。退后两步，认真看。你可能会发现之前忽略的关键信息。",
            "火雷噬嗑": "噬嗑是咬合、咬断。有个障碍卡在中间，你必须把它清除。这需要一次果断的决策——不能拖。",
            "山火贲": "贲是装饰。你关注了太多表面的事——好看但没用。回到本质，外表不重要。",
            "山地剥": "剥是层层剥落。你正在失去一些东西——工作、关系、健康。先接受这个事实，然后问：剩下什么是我能守住的？",
            "地雷复": "复是一阳来复。最糟的时候过去了，开始往好的方向转。冬天过后就是春天。给自己一点时间，做好准备。",
            "天雷无妄": "无妄是不妄为。别走捷径、别投机。老老实实做事，反而不会有事。本分是最好的策略。",
            "山天大畜": "大畜是积蓄很厚。之前的积累现在派上用场了。不是爆发，是稳稳地释放能量。",
            "山雷颐": "颐是颐养、养生。身体在给你发信号了。好好吃饭、好好睡觉。修整好了再出发。",
            "泽风大过": "大过就是过了头。你现在做的某件事已经超了。退回来一点，找一个平衡点。",
            "坎为水": "坎是险阻。困难是真实的，不是你想多了。但水再深也能渡过去——关键是找到对的方法和时机。",
            "离为火": "离是火，是光明，也是依附。你需要一个载体——就像火焰需要灯芯。找一个能支撑你的人或平台。",
        }
        return DETAILED_GUA.get(name, f"这是一个关于{name}的卦象。请结合你的具体处境来理解卦的指引——卦不会替你决定，但会帮你看到你没注意到的角度。")

    def _explain_change(self, from_name: str, to_name: str) -> str:
        """解释变卦含义"""
        return f"卦象从{from_name}变为{to_name}，说明你问的这件事不是固定的结果。变爻所在的位置就是改变的关键节点——主动做出调整，方向就会改变。"

    def _generate_advice(self, hex_name: str, topic: str, has_change: bool) -> str:
        """针对不同问题类型生成具体白话建议"""
        advice_map = {
            ("乾为天","事业"): "事业运势强劲。建议：1）接下来三个月全力冲刺，不要犹豫；2）主动牵头一个项目或会议，让更多人看到你的能力；3）注意不要独断——团队的意见可能比你想象的有价值。乾卦属金，刚极易折——对下属和同事留三分余地。",
            ("坤为地","事业"): "现在不是跳槽或大动作的好时机。建议：1）把手中每一件小事做到极致；2）主动帮同事分担工作，积累人情口碑；3）利用这段时间学一项新技能。你的价值会在稳定中体现出来。",
            ("水雷屯","事业"): "万事开头难。你现在的方向是对的，但需要更多耐心。建议：1）把大目标拆成每周的小目标，一步一步来；2）找到一个有过类似经历的人请教；3）准备好前半年可能看不到明显成果的心理预期。种子发芽前都在土里。",
            ("地天泰","事业"): "时机极佳！上下关系都通畅，想做的事有人支持。建议：1）未来三个月是黄金窗口，大胆推进拖延的项目；2）主动向上沟通你的想法，支持率会很高；3）唯一提醒：顺境时容易忽略细节，把每个环节检查两遍。",
            ("天地否","事业"): "你现在可能觉得处处碰壁。问题往往出在沟通上。建议：1）这周主动约一个关键的对话——把误会解开；2）试试换一种方式表达你的想法（书面代替口头，或反过来）；3）不要在这段时间做重大人事决策。",
            ("坎为水","事业"): "正处在困难期，这不可怕。水再深也有底。建议：1）把大目标拆成10个小步骤，每天完成一个；2）找有经验的人带你一段时间；3）避开未来30天内做重大职业决定——等水清了再走。",
            ("地雷复","事业"): "低谷已经过去了，接下来慢慢回暖。建议：1）现在是最好的准备期——更新简历、学新技术、拓展人脉；2）跟失联的老同事老客户重新建立联系；3）保持低调，不要跟任何人抱怨现状。春天来的时候你才接得住。",
            ("乾为天","感情"): "感情运势明朗。单身者近期有机会遇到合适的人——多参加行业活动或朋友聚会。有伴侣的，关系在上升期。乾卦属金，太刚则伤——温柔表达比强势争论有效十倍。",
            ("坤为地","感情"): "感情是细水长流的事，不要急。建议：1）先学会对自己好——你值得被爱；2）有伴侣的，多陪伴少说教；3）单身的，从兴趣爱好圈子里自然认识人。",
            ("泽雷随","感情"): "缘分来了就接住，缘分走了就放手。不要强求一个人留下。随卦的智慧是：顺其自然的感情才长久。这段时间把注意力放在自己的生活上。",
            ("水火既济","事业"): "事情快做成了，就差最后一步。这时候最容易出错——因为你觉得十拿九稳了。建议：最后关头加倍小心，把每一个细节检查三遍。不要提前庆祝。",
            ("火水未济","事业"): "事情还没成。但卦象中火往上、水往下——虽然现在位置不对，但终会相遇。你的努力不会白费。建议：1）复盘哪里卡住了；2）求助一个外部的人来帮你破局；3）给自己设定一个明确的时间节点，到点再评估。",
            ("地天泰","感情"): "天地交泰，感情运势极好。两个人沟通顺畅，心心相印。单身者容易遇到正缘——多出去走走。记住：好运气来的时候，主动一点，别等对方先迈步。",
            ("兑为泽","财运"): "兑卦主口舌和交易。财运来自沟通交流——多参加行业交流、朋友聚会，信息就是机会。但同时兑也主耗散——这个月做一个预算，不该花的一分别碰。",
            ("风火家人","感情"): "家人卦讲的是家庭和谐。你的感情问题可能需要回到家庭这个原点——跟父母聊聊、多陪陪家人。家和万事兴。",
            ("雷天大壮","事业"): "势头很强。现在冲一把是好的。但大壮卦警告：用80%的力量冲刺，留20%余地。撞上南墙再回头就来不及了。",
            ("震为雷","事业"): "雷卦主震动、变化。你可能面临一个突发事件或突然的变动。建议：1）保持冷静，不要被情绪带跑；2）先观察再行动，至少等24小时再做决定；3）变动中往往藏着机会——注意别人忽略的角落。",
            ("火天大有","财运"): "丰收的时机到了。之前的投资或努力即将有回报。建议：1）见好就收，不要贪；2）收获后先存三成，再想怎么花；3）跟对你有帮助的人分享成果——这会带来下一轮机会。",
        }

        key = (hex_name, topic)
        if key in advice_map:
            return advice_map[key]

        # 通用建议
        general_map = {
            "事业": f"你问的是事业方面的事。{hex_name}卦提醒你：先看清自己现在处在哪个阶段——是起步、上升、还是瓶颈期？不同阶段的策略完全不同。保持定力，不要被周围人的节奏带偏。",
            "感情": f"你问的是感情方面的事。{hex_name}卦告诉你：感情的事急不来。向内看比向外求更重要——你自己的状态决定了你能遇到什么样的人。",
            "财运": f"你问的是财运方面的事。{hex_name}卦的提示：君子爱财，取之有道。看看你的收入渠道——哪一条是可持续的？哪一条是靠运气的？把重心放在前者。",
            "学业": f"你问的是学业方面的事。{hex_name}卦说：学习的本质是积累。不要跟别人比速度，跟自己比进步。找到适合你的学习方法比报十个班有用。",
            "健康": f"你问的是健康方面的事。{hex_name}卦提醒：身体不会突然变差，也不会突然变好。每天的微小选择决定了三个月后的状态。从今天开始改变一个小习惯。",
            "综合": f"{hex_name}卦给你的启示：事情都有它的节奏，快不了也慢不了。你现在最需要的，是静下心来把眼前的事做好。",
        }
        return general_map.get(topic, general_map["综合"])

    # ===== 五行调和系统 =====

    def _build_wuxing_advice(self, r: HexagramResult) -> dict:
        """构建五行调和具体举措"""
        element = r.original_element
        colors = WUXING_COLORS.get(element, ["白"])
        items = WUXING_ITEMS.get(element, ["随身饰品"])
        actions = WUXING_ACTIONS.get(element, ["保持平和心态"])

        # 如果卦象偏凶（如火水未济、坎为水、天地否等），检查是否需要泄或补
        tension_hexagrams = {"坎为水":"水势太险，宜用木泄水、用土制水",
                            "天地否":"天地不交，宜用火暖局、用木疏通",
                            "火水未济":"火水不济，宜用木为桥梁",
                            "天水讼":"金气过刚，宜用水泄金、用火制金",
                            "山地剥":"土重埋金，宜用木疏土",
                            "泽水困":"金水相生而困，宜用火破局",
                            "离为火":"火势过旺，宜用水制火、用土泄火",
                            "震为雷":"木气动荡，宜用金制木以求稳",
        }

        tension_note = tension_hexagrams.get(r.original_name, "")

        return {
            "element": element,
            "direction": r.direction,
            "colors": colors,
            "items": items[:3],
            "actions": actions[:3],
            "tension_note": tension_note,
            "principle": f"卦象五行属{element}。{'若卦象偏旺，则需要泄其过旺之气；若卦象偏弱，则需要补其不足。' if tension_note else '调和五行的核心是平衡——不足则补，过旺则泄。'}",
        }

    # ===== 梅花易数时间起卦 =====

    def divine_by_time(self, question: str) -> HexagramResult:
        """时间起卦（梅花易数）: 年月日时 → 上卦+下卦+动爻 + 体用生克"""
        import datetime
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour

        shang = (year + month + day) % 8 or 8
        xia = (year + month + day + hour) % 8 or 8
        dongyao = (year + month + day + hour) % 6 or 6

        shang_gua = self.BAGUA_NUM[shang]
        xia_gua = self.BAGUA_NUM[xia]
        shang_wx = self.BAGUA_WUXING.get(shang_gua[0], "")
        xia_wx = self.BAGUA_WUXING.get(xia_gua[0], "")

        # 体用关系
        if dongyao <= 3:
            ti_gua = xia_gua[0]
            yong_gua = shang_gua[0]
            ti_pos = "下卦"
        else:
            ti_gua = shang_gua[0]
            yong_gua = xia_gua[0]
            ti_pos = "上卦"

        ti_wx = self.BAGUA_WUXING.get(ti_gua, "")
        yong_wx = self.BAGUA_WUXING.get(yong_gua, "")

        sk = self.SHENG_KE.get((ti_wx, yong_wx), None)
        sk_rev = self.SHENG_KE.get((yong_wx, ti_wx), None)

        if sk == "生":
            ti_yong_desc = f"用生体（{yong_wx}生{ti_wx}）：大吉之象，外部环境对你有利，事情容易成功。就像水滋养木——顺应时机，事半功倍。"
        elif sk_rev == "生":
            ti_yong_desc = f"体生用（{ti_wx}生{yong_wx}）：需要你主动付出，消耗较大。就像木生火——你付出的能量会转化为结果，但要注意不要透支自己。"
        elif sk == "克":
            ti_yong_desc = f"体克用（{ti_wx}克{yong_wx}）：事情可以办成但需要耗费心力去掌控局面。就像金克木——你有能力，但不要用力过猛。"
        elif sk_rev == "克":
            ti_yong_desc = f"用克体（{yong_wx}克{ti_wx}）：外部环境对你不利，宜谨慎行事。就像火克金——先保全自己，等待时机再行动。"
        else:
            ti_yong_desc = f"体用比和（{ti_wx}与{yong_wx}同五行）：内外和谐，事情顺利。双方力量相当，合作愉快。"

        code = self._tri_grams_to_code(xia, shang, dongyao)
        result = self._build_result(question, code, [dongyao - 1], shang_gua, xia_gua, ti_yong_desc)
        return result

    def divine_by_number(self, question: str, n1: int, n2: int, n3: int = 0) -> HexagramResult:
        """数字起卦（梅花易数）: 两个或三个数字 → 上卦+下卦+动爻"""
        shang = n1 % 8 or 8
        xia = n2 % 8 or 8
        dongyao = (n3 % 6 or 6) if n3 else ((n1 + n2) % 6 or 6)

        shang_gua = self.BAGUA_NUM[shang]
        xia_gua = self.BAGUA_NUM[xia]

        code = self._tri_grams_to_code(xia, shang, dongyao)
        return self._build_result(question, code, [dongyao - 1], shang_gua, xia_gua, "")

    def _tri_grams_to_code(self, xia_num: int, shang_num: int, dongyao: int) -> str:
        """八卦数 → 六爻二进制码"""
        trigram_map = {1:"111",2:"011",3:"101",4:"001",5:"110",6:"010",7:"100",8:"000"}
        xia_code = trigram_map.get(xia_num, "000")
        shang_code = trigram_map.get(shang_num, "000")
        return xia_code + shang_code

    def _build_result(self, question, code, changing, shang_gua=None, xia_gua=None, ti_yong_desc="") -> HexagramResult:
        """构建结果"""
        original = GUACI.get(code, {"name":"未识别的卦","meaning":"—","advice":"—","element":"—","direction":"—"})
        result = HexagramResult(
            question=question,
            original_code=code,
            original_name=original.get("name",""),
            original_meaning=original.get("meaning",""),
            original_advice=original.get("advice",""),
            original_element=original.get("element",""),
            direction=original.get("direction",""),
            changing_lines=changing,
        )
        result.analysis = self._analyze(result)
        if ti_yong_desc:
            result.analysis += f"\n\n⚡ 体用关系：{ti_yong_desc}"
        result.suggestion = self._suggest(result)
        result.wuxing_advice = self._build_wuxing_advice(result)
        # 如果有体用生克，也加入五行建议
        if ti_yong_desc and "用克体" in ti_yong_desc:
            result.wuxing_advice["tension_note"] = "用克体，外部压力较大。建议增强体卦五行以抵御压力。" + result.wuxing_advice.get("tension_note", "")
        return result

    def get_hexagram_display(self, code: str) -> dict:
        """获取卦象展示数据"""
        yao_names = {0:"初",1:"二",2:"三",3:"四",4:"五",5:"上"}
        lines = []
        for i, c in enumerate(code):
            lines.append({
                "position": yao_names.get(i, str(i+1)),
                "type": "阳爻 ———" if c == "1" else "阴爻 — —",
                "is_yang": c == "1",
            })
        return {"lines": list(reversed(lines))}
