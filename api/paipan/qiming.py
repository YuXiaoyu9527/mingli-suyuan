"""
八字起名引擎
============
根据父母八字分析五行缺补，推荐起名用字。

原理：结合父母八字用神+五行平衡，推荐相应五行的汉字。

用法:
  from api.paipan.qiming import QimingEngine
  engine = QimingEngine()
  names = engine.generate(father_bazi, mother_bazi, surname="李", gender="男")
"""

from dataclasses import dataclass, field
from .data.ganzhi import GAN_WUXING
from .yongshen import YongshenEngine


# 五行汉字推荐库（精选常用起名用字）
WUXING_CHARS = {
    "木": {
        "male": ["林","森","柏","松","桐","楠","楷","栋","杰","彬","楚","桓","栩","槿","荣"],
        "female": ["琳","柳","梅","樱","桐","楠","槿","蕊","萱","芝","菲","若","艺","茉","荷"],
    },
    "火": {
        "male": ["煜","烨","炫","焕","昊","旭","晨","晟","曜","朗","明","昭","昱","晖","炜"],
        "female": ["煜","烨","炫","灵","丹","彤","晓","昕","璐","璐","瑾","瑶","璇","昭","旻"],
    },
    "土": {
        "male": ["坤","均","城","基","坚","坦","培","圣","宇","安","屹","峥","磊","岩","峰"],
        "female": ["婉","娴","怡","悦","恩","怡","韵","岚","雅","伊","依","宛","安","媛","瑛"],
    },
    "金": {
        "male": ["铭","锐","钧","锋","铮","鑫","镇","锡","铠","锦","钧","钦","铭","铮","瑞"],
        "female": ["钰","铭","锐","锦","铃","银","钰","珊","珠","瑞","琪","琳","珍","琬","琛"],
    },
    "水": {
        "male": ["涵","浩","泽","润","渊","涛","瀚","清","源","江","海","洋","涵","沛","霖"],
        "female": ["涵","洁","澜","漫","汐","沐","洛","淇","淑","湘","滢","漫","澜","清","渊"],
    },
}

# 五格数理简表（天格/人格/地格 吉凶参考）
WUXING_SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
WUXING_KE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}


@dataclass
class QimingResult:
    """起名结果"""
    surname: str
    gender: str

    # 父母八字五行分析
    father_rizhu: str
    mother_rizhu: str
    father_yongshen: list
    mother_yongshen: list
    recommended_wuxing: list  # 推荐的五行
    wuxing_reason: str        # 推荐原因

    # 推荐名字
    suggestions: list = field(default_factory=list)


class QimingEngine:
    """起名引擎"""

    def generate(self, father, mother, surname="李", gender="男") -> QimingResult:
        """根据父母八字生成起名建议"""
        # 1. 分析父母用神
        ys = YongshenEngine()
        f_ys = ys.analyze(father)
        m_ys = ys.analyze(mother)

        # 2. 综合推荐五行
        # 优先：双方都用神都指向的五行
        # 其次：补最弱的那一方的用神
        f_set = set(f_ys.recommended)
        m_set = set(m_ys.recommended)
        common = f_set & m_set

        result = QimingResult(
            surname=surname,
            gender=gender,
            father_rizhu=f"{father.rizhu}({father.rizhu_wuxing})",
            mother_rizhu=f"{mother.rizhu}({mother.rizhu_wuxing})",
            father_yongshen=f_ys.recommended,
            mother_yongshen=m_ys.recommended,
            recommended_wuxing=[],
            wuxing_reason="",
        )

        if common:
            result.recommended_wuxing = list(common)
            result.wuxing_reason = f"双方用神均指向{'、'.join(common)}，以此为孩子命名首选"
        else:
            # 各取第一用神
            result.recommended_wuxing = [f_ys.recommended[0], m_ys.recommended[0]]
            result.wuxing_reason = f"父亲用神{'、'.join(f_ys.recommended)}，母亲用神{'、'.join(m_ys.recommended)}，各取第一用神"

        # 3. 生成名字建议
        char_gender = "male" if gender == "男" else "female"

        # 单字名
        for wx in result.recommended_wuxing[:3]:
            if wx in WUXING_CHARS:
                chars = WUXING_CHARS[wx][char_gender]
                for ch in chars[:3]:
                    # 检查五格（简化：笔画取近似值）
                    result.suggestions.append({
                        "name": f"{surname}{ch}",
                        "wuxing": wx,
                        "structure": "单字名",
                        "meaning": f"{wx}行属性，{'父母双用神' if wx in common else '补'+('父' if wx == f_ys.recommended[0] else '母')+'方用神'}",
                    })

        # 双字名（搭配第二用神）
        for wx1 in result.recommended_wuxing[:2]:
            for wx2 in result.recommended_wuxing[:2]:
                if wx1 == wx2:
                    continue
                if wx1 in WUXING_CHARS and wx2 in WUXING_CHARS:
                    c1 = WUXING_CHARS[wx1][char_gender][0]
                    c2 = WUXING_CHARS[wx2][char_gender][1]
                    result.suggestions.append({
                        "name": f"{surname}{c1}{c2}",
                        "wuxing": f"{wx1}+{wx2}",
                        "structure": "双字名",
                        "meaning": f"二字分属{wx1}和{wx2}，五行互补、阴阳平衡",
                    })

        return result
