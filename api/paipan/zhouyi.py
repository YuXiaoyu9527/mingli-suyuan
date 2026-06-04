"""
周易占卜引擎
============
六爻起卦 + 64卦解读。

起卦方法：随机生成六爻（每爻为阴/阳/变爻）
解读：基于卦辞/爻辞，结合所求问题分析

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

    analysis: str = ""             # 综合分析
    suggestion: str = ""           # 建议


class ZhouyiEngine:
    """周易占卜引擎（整合梅花易数）"""

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
        """起卦占卜"""
        # 1. 随机生成六爻
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

        # 2. 本卦（从下往上排列：code_parts[0]是最下面一爻）
        original_code = "".join(code_parts)  # 下→上
        original = GUACI.get(original_code, {"name":"未识别的卦","meaning":"—","advice":"—"})

        # 3. 变卦（变爻取反）
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

        # 4. 综合分析
        result.analysis = self._analyze(result)
        result.suggestion = self._suggest(result)

        return result

    def _analyze(self, r: HexagramResult) -> str:
        """分析卦象"""
        parts = [f"你问「{r.question}」，占得{r.original_name}。"]

        if r.changing_lines:
            positions = "、".join(f"第{p+1}爻" for p in r.changing_lines)
            parts.append(f"有变爻{positions}，变为{r.changed_name}。")
            parts.append(f"本卦：{r.original_meaning}。变卦：{r.changed_meaning}。")
        else:
            parts.append(f"卦义：{r.original_meaning}。")

        parts.append(f"此卦属{r.original_element}行，利{r.direction}方。")

        return "".join(parts)

    def _suggest(self, r: HexagramResult) -> str:
        """给出建议"""
        # 根据卦的吉凶给建议
        auspicious = ["泰","大有","谦","豫","随","临","观","复","恒","大壮","晋","升","鼎","既济"]
        inauspicious = ["否","剥","坎","困","蹇","大过","明夷","未济"]

        if any(a in r.original_name for a in auspicious):
            return f"{r.original_advice}。此卦大吉，宜把握时机。"
        elif any(a in r.original_name for a in inauspicious):
            if r.changing_lines:
                return f"{r.original_advice}。虽有波折，但变爻出现，情况会好转。宜保持信心，积极应对。"
            return f"{r.original_advice}。宜守正待时，不宜轻举妄动。"
        else:
            return f"{r.original_advice}。中庸之道，顺其自然即可。"

    def divine_by_time(self, question: str) -> HexagramResult:
        """时间起卦（梅花易数）: 年月日时 → 上卦+下卦+动爻"""
        import datetime
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour

        # 上卦 = (年+月+日) % 8
        shang = (year + month + day) % 8 or 8
        # 下卦 = (年+月+日+时) % 8
        xia = (year + month + day + hour) % 8 or 8
        # 动爻 = (年+月+日+时) % 6
        dongyao = (year + month + day + hour) % 6 or 6

        shang_gua = self.BAGUA_NUM[shang]
        xia_gua = self.BAGUA_NUM[xia]
        shang_wx = self.BAGUA_WUXING.get(shang_gua[0], "")
        xia_wx = self.BAGUA_WUXING.get(xia_gua[0], "")

        # 体用关系：无动爻的卦为体，有动爻的卦为用
        if dongyao <= 3:
            ti_gua = xia_gua[0]  # 下卦为体
            yong_gua = shang_gua[0]  # 上卦为用
        else:
            ti_gua = shang_gua[0]  # 上卦为体
            yong_gua = xia_gua[0]  # 下卦为用

        ti_wx = self.BAGUA_WUXING.get(ti_gua, "")
        yong_wx = self.BAGUA_WUXING.get(yong_gua, "")

        # 体用生克
        sk = self.SHENG_KE.get((ti_wx, yong_wx), None)
        sk_rev = self.SHENG_KE.get((yong_wx, ti_wx), None)

        if sk == "生":
            ti_yong_desc = f"用生体（{yong_wx}生{ti_wx}）：大吉，事易成"
        elif sk_rev == "生":
            ti_yong_desc = f"体生用（{ti_wx}生{yong_wx}）：泄气，需付出较多"
        elif sk == "克":
            ti_yong_desc = f"体克用（{ti_wx}克{yong_wx}）：事可成但费力"
        elif sk_rev == "克":
            ti_yong_desc = f"用克体（{yong_wx}克{ti_wx}）：不吉，宜小心行事"
        else:
            ti_yong_desc = f"体用比和（{ti_wx}与{yong_wx}同五行）：和谐顺利"

        # 生成卦码（下卦→上卦，下卦爻在前）
        code = self._tri_grams_to_code(xia, shang, dongyao)
        return self._build_result(question, code, [5 - dongyao + 1], shang_gua, xia_gua, ti_yong_desc)

    def divine_by_number(self, question: str, n1: int, n2: int, n3: int = 0) -> HexagramResult:
        """数字起卦（梅花易数）: 两个或三个数字 → 上卦+下卦+动爻"""
        shang = n1 % 8 or 8
        xia = n2 % 8 or 8
        dongyao = (n3 % 6 or 6) if n3 else ((n1 + n2) % 6 or 6)

        shang_gua = self.BAGUA_NUM[shang]
        xia_gua = self.BAGUA_NUM[xia]

        code = self._tri_grams_to_code(xia, shang, dongyao)
        return self._build_result(question, code, [5 - dongyao + 1], shang_gua, xia_gua, "")

    def _tri_grams_to_code(self, xia_num: int, shang_num: int, dongyao: int) -> str:
        """八卦数 → 六爻二进制码"""
        trigram_map = {1:"111",2:"011",3:"101",4:"001",5:"110",6:"010",7:"100",8:"000"}
        xia_code = trigram_map.get(xia_num, "000")
        shang_code = trigram_map.get(shang_num, "000")
        return xia_code + shang_code  # 下卦在前

    def _build_result(self, question, code, changing, shang_gua=None, xia_gua=None, ti_yong_desc="") -> HexagramResult:
        """构建结果"""
        original = GUACI.get(code, {"name":"未识别的卦","meaning":"—","advice":"—"})
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
            result.analysis += f" 体用关系：{ti_yong_desc}。"
        result.suggestion = self._suggest(result)
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
        return {"lines": list(reversed(lines))}  # 从上往下显示
