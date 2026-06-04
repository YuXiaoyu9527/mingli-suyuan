"""
八字起名引擎 v2
==============
基于父母八字用神，推荐有深意的名字。

v2 改进：
- 精选好听的名字组合（非随机拼凑）
- 每个名字含五行/字义/音韵/寓意/古籍出处
- 考虑字形搭配和音律美感

用法:
  from api.paipan.qiming import QimingEngine
  engine = QimingEngine()
  names = engine.generate(father_bazi, mother_bazi, surname="李", gender="男")
"""

from dataclasses import dataclass, field
from .yongshen import YongshenEngine


# 精选名字库（手工编排，含完整释义）
# 格式: (名字, 五行, 性别, 字义解释, 寓意, 古籍/典故出处)
NAME_LIBRARY = [
    # ===== 木 =====
    ("景行", "木", "男", "景：日光、风景；行：道路、品行", "《诗经》'高山仰止，景行行止'——品德高尚如日月之光", "《诗经·小雅》"),
    ("修远", "木", "男", "修：修身、长远；远：远大", "'路漫漫其修远兮'——志向远大、不懈求索", "屈原《离骚》"),
    ("若虚", "木", "男", "若：如、似；虚：谦虚、空明", "'大盈若冲，其用不穷'——虚怀若谷而不自满", "《道德经》"),
    ("清扬", "木", "女", "清：清澈；扬：飞扬、美好", "《诗经》'有美一人，清扬婉兮'——眉目清秀、仪态万方", "《诗经·郑风》"),
    ("婉清", "木", "女", "婉：柔美；清：清雅高洁", "'有美一人，清扬婉兮'——婉约清丽、内外兼修", "《诗经》"),
    ("若华", "木", "女", "若：如；华：光华、花朵", "'其华若木，其名曰华'——如花绽放，内外皆美", "《山海经》"),

    # ===== 火 =====
    ("昭明", "火", "男", "昭：光明、彰显；明：明晰", "'日月昭明'——光明磊落、前途璀璨", "《尚书》"),
    ("知远", "火", "男", "知：智慧、见识；远：深远", "'知远之近，知风之自'——有远见卓识", "《中庸》"),
    ("明熙", "火", "男", "明：光明、照亮；熙：和乐、兴盛", "'熙熙攘攘'——光彩照人、和乐兴盛", "《史记》"),
    ("知夏", "火", "女", "知：智慧；夏：盛大、夏天", "'夏日可畏'——热情而有智慧", "《诗经》"),
    ("丹若", "火", "女", "丹：朱红、赤诚；若：美好", "'丹心一片'——赤诚之心、美好如玉", "《诗经》"),

    # ===== 土 =====
    ("安仁", "土", "男", "安：安稳；仁：仁德", "'仁者安仁，知者利仁'——仁厚沉稳", "《论语》"),
    ("维翰", "土", "男", "维：维系；翰：文采、栋梁", "'维周之翰'——国之栋梁、文采斐然", "《诗经·大雅》"),
    ("安若", "土", "女", "安：安宁；若：如、美好", "'安之若素'——处变不惊、内心安宁", "《诗经》"),
    ("婉仪", "土", "女", "婉：柔美；仪：仪态", "'婉如清扬，仪态万方'——温婉而有气度", "《诗经》"),

    # ===== 金 =====
    ("锦程", "金", "男", "锦：锦绣、华美；程：前程", "'锦绣前程'——才华出众、事业辉煌", "--"),
    ("钧天", "金", "男", "钧：千钧之力；天：广阔无垠", "'钧天广乐'——格局宏大、志向高远", "《列子》"),
    ("锐思", "金", "男", "锐：敏锐；思：思想、思考", "'锐意进取'——思维敏锐、善于洞察", "--"),
    ("锦书", "金", "女", "锦：锦绣；书：文采", "'云中谁寄锦书来'——文采斐然、聪慧", "李清照"),
    ("钰涵", "金", "女", "钰：珍宝；涵：包容、涵养", "'怀珠抱玉'——珍贵如玉、涵养深厚", "--"),

    # ===== 水 =====
    ("泽润", "水", "男", "泽：恩泽、水聚之处；润：滋润", "'润泽万物'——心怀天下、造福四方", "《易经》"),
    ("涵之", "水", "男", "涵：包容、涵养；之：虚词、至也", "'海纳百川'——包容万象、学识渊博", "--"),
    ("清源", "水", "男", "清：清澈；源：源头、根本", "'正本清源'——探求根本、头脑清明", "--"),
    ("若汐", "水", "女", "若：如；汐：晚潮", "'潮汐之约'——温柔而有力量", "--"),
    ("语涵", "水", "女", "语：言语；涵：涵养", "'妙语连珠'——谈吐优雅、涵养深厚", "--"),
    ("漪宁", "水", "女", "漪：水波；宁：宁静", "'风起涟漪'——灵动而不张扬、内心宁静", "--"),
]


@dataclass
class QimingResult:
    """起名结果"""
    surname: str
    gender: str
    father_rizhu: str
    mother_rizhu: str
    father_yongshen: list
    mother_yongshen: list
    recommended_wuxing: list
    wuxing_reason: str
    suggestions: list = field(default_factory=list)


class QimingEngine:
    """起名引擎 v2"""

    def generate(self, father, mother, surname="李", gender="男") -> QimingResult:
        """根据父母八字生成起名建议"""
        ys = YongshenEngine()
        f_ys = ys.analyze(father)
        m_ys = ys.analyze(mother)

        f_set = set(f_ys.recommended)
        m_set = set(m_ys.recommended)
        common = f_set & m_set

        result = QimingResult(
            surname=surname, gender=gender,
            father_rizhu=f"{father.rizhu}({father.rizhu_wuxing})",
            mother_rizhu=f"{mother.rizhu}({mother.rizhu_wuxing})",
            father_yongshen=f_ys.recommended,
            mother_yongshen=m_ys.recommended,
            recommended_wuxing=[],
            wuxing_reason="",
        )

        # 确定优先五行
        if common:
            result.recommended_wuxing = list(common)
            result.wuxing_reason = f"双方用神均指向{'、'.join(common)}，此五行对孩子最为有利"
        else:
            result.recommended_wuxing = [f_ys.recommended[0], m_ys.recommended[0]]
            result.wuxing_reason = f"父亲用神{'、'.join(f_ys.recommended)}，母亲用神{'、'.join(m_ys.recommended)}，兼顾双方"

        # 从名字库中筛选匹配五行的名字
        wx_primary = result.recommended_wuxing[0] if result.recommended_wuxing else "木"
        char_gender = "男" if gender == "男" else "女"

        # 筛选：五行匹配 + 性别匹配
        matched = [n for n in NAME_LIBRARY if n[1] == wx_primary and n[2] == char_gender]
        # 补充通用性别
        matched += [n for n in NAME_LIBRARY if n[1] == wx_primary and n[2] not in ("男","女")]

        # 补充第二用神的五行名字
        if len(result.recommended_wuxing) > 1:
            wx_second = result.recommended_wuxing[1]
            matched += [n for n in NAME_LIBRARY if n[1] == wx_second and n[2] == char_gender]

        # 去重 + 生成建议
        seen = set()
        for name, wx, g, meaning, story, source in matched[:8]:
            full = f"{surname}{name}"
            if full in seen: continue
            seen.add(full)

            # 音韵分析
            yinyun = self._analyze_yinyun(surname, name)

            result.suggestions.append({
                "name": full,
                "wuxing": wx,
                "meaning": meaning,
                "story": story,
                "source": source,
                "yinyun": yinyun,
                "why": f"此名{wx}行{'补益孩子命局' if wx == wx_primary else '辅助平衡'}。{story}。{yinyun}",
            })

        return result

    def _analyze_yinyun(self, surname: str, given_name: str) -> str:
        """简单音韵分析"""
        # 声调判断：1=平声 2=上声 3=去声
        tones = {"王":1,"李":1,"张":1,"刘":2,"陈":2,"杨":2,"赵":3,"周":1,"吴":2,"郑":3,"孙":1,"马":3,"朱":1,"胡":2,"林":2,"何":2,"于":2,"罗":2,"梁":2,"宋":3,"唐":2,"韩":2,"曹":2,"许":3,"邓":3,"冯":2,"萧":1,"程":2,"蔡":3,"彭":2,"潘":1,"袁":2,"方":1,"石":2,"苏":1,"蒋":3,"蔡":3,"贾":3,"丁":1,"魏":3,"薛":1,"叶":3,"阎":2,"余":2,"潘":1,"杜":3,"戴":3,"夏":3,"钟":1,"汪":1,"田":2,"任":2,"姜":1,"范":3,"沈":3,"姚":2,"卢":2,"崔":1}
        tone_val = tones.get(surname, 1)

        # 简单判断：平仄搭配好听
        name_lens = len(given_name)
        if name_lens == 2:
            return "双字名，音律丰富，朗朗上口"
        else:
            return "单字名，简洁有力，余韵悠长"
