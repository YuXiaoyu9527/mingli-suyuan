"""
命理溯源 - 统一API服务
======================
FastAPI 服务器，整合排盘引擎 + RAG检索 + AI解读。

启动:
  uvicorn api.server:app --reload --port 8000

环境变量（可选，在 .env 文件中配置）:
  DEEPSEEK_API_KEY    DeepSeek API密钥
  DEEPSEEK_BASE_URL   API地址（默认 https://api.deepseek.com/v1）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="命理溯源 API",
    description="八字排盘 + 古籍RAG检索 + AI解读",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 模型定义 =====

class PaipanRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    gender: str = "男"
    city: str = ""  # 出生城市（用于真太阳时校正）


class JianpiRequest(BaseModel):
    """简批请求：排盘参数 + 是否启用AI"""
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    gender: str = "男"
    use_ai: bool = True


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source: Optional[str] = None


class MentorRequest(BaseModel):
    question: str
    student_answer: str
    correct_answer: str


class MingliRequest(BaseModel):
    pattern: Optional[str] = None  # 按格局筛选
    search: Optional[str] = None   # 搜索关键词


class QimingRequest(BaseModel):
    f_year: int = 1990; f_month: int = 5; f_day: int = 20; f_hour: int = 12
    m_year: int = 1992; m_month: int = 8; m_day: int = 15; m_hour: int = 10
    surname: str = "李"; gender: str = "男"


class ZhouyiRequest(BaseModel):
    question: str = "我想问事业"


class HehunRequest(BaseModel):
    # 男方
    m_year: int = 1990; m_month: int = 5; m_day: int = 20
    m_hour: int = 12; m_minute: int = 0
    # 女方
    f_year: int = 1992; f_month: int = 8; f_day: int = 15
    f_hour: int = 10; f_minute: int = 0


class FengshuiRequest(BaseModel):
    door_direction: str = ""       # 大门朝向
    kitchen: str = ""              # 厨房位置
    bedroom: str = ""              # 主卧位置
    bathroom: str = ""             # 卫生间位置
    living_room: str = ""          # 客厅位置
    missing_corners: list = []     # 缺角: ["西北","东南"]
    xingsha: list = []             # 形煞: ["路冲","穿堂煞"]


class ZejiRequest(BaseModel):
    activity: str = "结婚"  # 结婚/搬家/开业/出行/动土
    days: int = 90          # 搜索未来多少天
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: int = 12
    gender: str = "男"


class LiunianRequest(BaseModel):
    # 出生信息
    birth_year: int = 1990
    birth_month: int = 5
    birth_day: int = 20
    birth_hour: int = 12
    gender: str = "男"
    # 要查的年份
    year: int = 2026
    month: Optional[int] = None  # 流月


class QuizRequest(BaseModel):
    chapter: Optional[str] = None  # 按章节筛选


class YijiRequest(BaseModel):
    """宜忌请求：可选用户八字"""
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: int = 12
    minute: int = 0
    gender: str = "男"


# ===== 懒加载单例 =====

_searcher = None
_interpreter = None


def get_searcher():
    global _searcher
    if _searcher is None:
        # 笔记本ONNX有DLL问题，直接用关键词搜索
        from api.rag.simple_search import SimpleSearcher
        _searcher = SimpleSearcher()
    return _searcher


def get_ai():
    global _interpreter
    if _interpreter is None:
        from api.ai import AIInterpreter
        _interpreter = AIInterpreter()
    return _interpreter


# ===== API 端点 =====

@app.get("/")
def root():
    return {"name": "命理溯源 API", "version": "0.1.0", "status": "ok"}


@app.post("/api/paipan")
def api_paipan(req: PaipanRequest):
    """八字排盘（纯代码，无AI）"""
    from api.paipan import paipan, to_dict

    hour, minute = req.hour, req.minute
    tz_offset = 0
    if req.city:
        from api.paipan.truesolar import correct_time
        hour, minute, tz_offset = correct_time(req.city, req.hour, req.minute)

    result = paipan(req.year, req.month, req.day, hour, minute, req.gender)
    data = to_dict(result)
    if req.city:
        data["true_solar"] = {
            "city": req.city,
            "original_time": f"{req.hour:02d}:{req.minute:02d}",
            "corrected_time": f"{hour:02d}:{minute:02d}",
            "offset_minutes": tz_offset,
        }
    return data


@app.get("/api/cities")
def api_cities():
    """获取支持真太阳时校正的城市列表"""
    from api.paipan.truesolar import get_city_list
    return {"cities": get_city_list()}


@app.post("/api/full-analysis")
def api_full_analysis(req: PaipanRequest):
    """全量分析：排盘+格局+用神+AI简批 一次返回"""
    from api.paipan import paipan, to_dict
    from api.paipan.geju import GejuEngine
    from api.paipan.yongshen import YongshenEngine

    # 真太阳时
    hour, minute = req.hour, req.minute
    tz_info = None
    if req.city:
        from api.paipan.truesolar import correct_time
        hour, minute, tz_offset = correct_time(req.city, req.hour, req.minute)
        tz_info = {"city": req.city, "offset": tz_offset,
                   "corrected": f"{hour:02d}:{minute:02d}"}

    bazi = paipan(req.year, req.month, req.day, hour, minute, req.gender)
    data = to_dict(bazi)

    # 格局
    geju = GejuEngine().determine(bazi)

    # 用神
    yongshen = YongshenEngine().analyze(bazi)

    # AI（可选）
    interpretation = None
    ancient_refs = None
    try:
        from api.rag.simple_search import SimpleSearcher
        searcher = SimpleSearcher()
        terms = f"{data['rizhu']}日主 {data['rizhu_wuxing']}"
        ancient_refs = searcher.search_for_ai(terms, top_k=2)
        from api.ai import AIInterpreter
        ai = AIInterpreter()
        interpretation = ai.jianpi(data, ancient_refs)
    except Exception:
        pass

    return {
        "paipan": data,
        "true_solar": tz_info,
        "geju": {
            "pattern": geju.pattern,
            "pattern_type": geju.pattern_type,
            "is_chengge": geju.is_chengge,
            "conditions": geju.chengge_conditions,
            "reasons": geju.baige_reasons,
            "analysis": geju.analysis,
        },
        "yongshen": {
            "wangshuai": yongshen.wangshuai,
            "wangshuai_reason": yongshen.wangshuai_reason,
            "recommended": yongshen.recommended,
            "jishen": yongshen.jishen,
            "analysis": yongshen.analysis,
        },
        "interpretation": interpretation,
        "ancient_refs": ancient_refs,
    }


@app.post("/api/jianpi")
def api_jianpi(req: JianpiRequest):
    """
    八字简批（排盘 + RAG检索 + AI解读，三层串联）

    流程：
    1. 代码排盘（Layer 2）
    2. 用日主+格局关键词检索古籍（Layer 3）
    3. AI基于排盘数据+古籍原文生成解读（Layer 4）
    """
    from api.paipan import paipan, to_dict

    # Step 1: 排盘
    result = paipan(req.year, req.month, req.day, req.hour, req.minute, req.gender)
    data = to_dict(result)

    # Step 2: 用日主五行+十神构造检索关键词
    rizhu = data["rizhu"]
    wuxing = data["rizhu_wuxing"]
    # 取前3个十神作为检索词
    shishen_items = sorted(data.get("shishen_count", {}).items(), key=lambda x: -x[1])
    search_terms = f"{rizhu}日主 {wuxing} " + " ".join(s[0] for s in shishen_items[:3])

    searcher = get_searcher()
    refs = searcher.search_for_ai(search_terms, top_k=3)

    # Step 3: AI解读
    response = {
        "paipan": data,
        "ancient_refs": refs,
        "interpretation": None,
    }

    if req.use_ai:
        ai = get_ai()
        response["interpretation"] = ai.jianpi(data, refs)

    return response


@app.post("/api/search")
def api_search(req: SearchRequest):
    """古籍原文检索"""
    searcher = get_searcher()
    results = searcher.search(req.query, top_k=req.top_k, filter_source=req.source)
    return {"query": req.query, "total": len(results), "results": results}


@app.post("/api/mentor")
def api_mentor(req: MentorRequest):
    """断案录AI导师"""
    searcher = get_searcher()
    # 从题目中提取关键词检索古籍
    refs = searcher.search_for_ai(req.question, top_k=2)

    ai = get_ai()
    hint = ai.mentor(req.question, req.student_answer, req.correct_answer, refs)

    return {"hint": hint, "refs": refs}


@app.post("/api/mingli")
def api_mingli(req: MingliRequest):
    """历史命例检索"""
    import json
    from pathlib import Path

    cases_file = Path(__file__).parent.parent / "data" / "mingli_cases.jsonl"
    if not cases_file.exists():
        return {"total": 0, "cases": []}

    cases = []
    with open(cases_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                c = json.loads(line)
                # 筛选
                if req.pattern and c.get("pattern") != req.pattern:
                    continue
                if req.search:
                    search_lower = req.search.lower()
                    match = (
                        search_lower in c.get("name", "").lower()
                        or search_lower in c.get("pattern", "").lower()
                        or search_lower in c.get("bazi", "").lower()
                        or search_lower in c.get("rishu", "").lower()
                        or any(search_lower in t.lower() for t in c.get("tags", []))
                    )
                    if not match:
                        continue
                cases.append(c)

    # 统计格局分布
    patterns = {}
    for c in cases:
        p = c.get("pattern", "未知")
        patterns[p] = patterns.get(p, 0) + 1

    return {
        "total": len(cases),
        "patterns": [
            {"name": p, "count": cnt}
            for p, cnt in sorted(patterns.items(), key=lambda x: -x[1])
        ],
        "cases": cases,
    }


@app.get("/api/sources")
def api_sources():
    """列出所有古籍来源"""
    return {
        "sources": [
            {"name": "三命通會", "volumes": "12卷", "records": 1654, "abbr": "smtm"},
            {"name": "滴天髓闡微", "volumes": "全篇", "records": 678, "abbr": "dts"},
            {"name": "淵海子平", "volumes": "全篇", "records": 102, "abbr": "yhp"},
            {"name": "欽定協紀辨方書", "volumes": "36卷", "records": 2445, "abbr": "xjbf"},
        ]
    }


@app.post("/api/yiji")
def api_yiji(req: YijiRequest):
    """
    完整老黄历 — 建除/黄道/冲煞/吉神方位/时辰吉凶/星宿/个人分析

    如果不传用户八字参数，只返回通用黄历。
    传入出生日期则叠加个人分析。
    """
    from datetime import datetime
    from lunar_python import Solar
    from api.paipan.yiji import DailyYiji

    now = datetime.now()
    solar = Solar.fromYmdHms(now.year, now.month, now.day, 12, 0, 0)

    user_bazi = None
    if req.year is not None:
        from api.paipan import paipan
        user_bazi = paipan(req.year, req.month or 1, req.day or 1,
                           req.hour, req.minute, req.gender)

    yj = DailyYiji()
    hl = yj.get_full_huangli(solar, user_bazi)

    # 每日开运建议
    daily_tips = None
    if user_bazi is not None:
        from api.paipan.yongshen import YongshenEngine
        from api.paipan.daily_tips import generate_from_bazi
        ys = YongshenEngine().analyze(user_bazi)
        tips = generate_from_bazi(hl.day_ganzhi, ys, hl.day_gan, hl.day_zhi)
        daily_tips = {
            "wear_colors": tips.wear_colors,
            "wear_detail": tips.wear_detail,
            "accessory": tips.accessory,
            "suggest_do": tips.suggest_do,
            "suggest_avoid": tips.suggest_avoid,
            "lucky_direction": tips.lucky_direction,
            "daily_quote": tips.daily_quote,
        }

    return {
        "date": hl.date,
        "lunar_date": hl.lunar_date,
        "day_ganzhi": hl.day_ganzhi,
        "day_gan": hl.day_gan,
        "day_zhi": hl.day_zhi,
        "shengxiao": hl.shengxiao,
        "week": hl.week,
        "jianchu": hl.jianchu,
        "xiu": hl.xiu,
        "xiu_luck": hl.xiu_luck,
        # 冲煞
        "chong_shengxiao": hl.chong_shengxiao,
        "chong_desc": hl.chong_desc,
        "sha_direction": hl.sha_direction,
        # 值神
        "tianshen": hl.tianshen,
        "tianshen_type": hl.tianshen_type,
        "tianshen_luck": hl.tianshen_luck,
        "jishen": hl.jishen,
        "xiongsha": hl.xiongsha,
        # 宜忌
        "yi": hl.yi,
        "ji": hl.ji,
        # 彭祖
        "pengzu_gan": hl.pengzu_gan,
        "pengzu_zhi": hl.pengzu_zhi,
        # 吉神方位
        "caishen": hl.caishen,
        "xishen": hl.xishen,
        "fushen": hl.fushen,
        "yanggui": hl.yanggui,
        "yingui": hl.yingui,
        # 胎神/九星
        "taishen": hl.taishen,
        "jiuxing": hl.jiuxing,
        # 时辰
        "hours": hl.hours,
        # 古籍参考
        "classical_ref": hl.classical_ref,
        # 个人
        "personal": hl.personal,
        # 开运建议
        "daily_tips": daily_tips,
    }


@app.post("/api/quiz")
def api_quiz(req: QuizRequest):
    """获取断案录题库"""
    import json
    from pathlib import Path

    quiz_file = Path(__file__).parent.parent / "data" / "quiz_cases.jsonl"
    if not quiz_file.exists():
        return {"total": 0, "chapters": [], "questions": []}

    questions = []
    with open(quiz_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                q = json.loads(line)
                if req.chapter and q.get("chapter") != req.chapter:
                    continue
                # 不返回正确答案
                questions.append({
                    "id": q["id"],
                    "chapter": q["chapter"],
                    "title": q["title"],
                    "difficulty": q["difficulty"],
                    "story": q["story"],
                    "question": q["question"],
                    "options": q["options"],
                })

    # 汇总章节信息
    chapters_set = {}
    for q in questions:
        ch = q["chapter"]
        chapters_set[ch] = chapters_set.get(ch, 0) + 1

    return {
        "total": len(questions),
        "chapters": [
            {"name": ch, "count": cnt}
            for ch, cnt in sorted(chapters_set.items())
        ],
        "questions": questions,
    }


@app.post("/api/quiz/check")
def api_quiz_check(req: dict):
    """校验答案"""
    import json
    from pathlib import Path

    quiz_id = req.get("id")
    user_answer = req.get("answer")
    quiz_file = Path(__file__).parent.parent / "data" / "quiz_cases.jsonl"

    with open(quiz_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                q = json.loads(line)
                if q["id"] == quiz_id:
                    correct = user_answer == q["correct"]
                    return {
                        "correct": correct,
                        "correct_answer": q["correct"],
                        "correct_text": q["options"][q["correct"]]["text"],
                        "classical_ref": q.get("classical_ref", ""),
                        "analysis": q.get("analysis", ""),
                    }

    return {"error": "题目未找到"}


@app.post("/api/liunian")
def api_liunian(req: LiunianRequest):
    """流年/流月推算（需传入出生日期）"""
    from api.paipan import paipan
    from api.paipan.liunian import LiunianEngine

    # 排盘
    user_bazi = paipan(req.birth_year, req.birth_month, req.birth_day, req.birth_hour)
    engine = LiunianEngine()

    # 流年
    year_report = engine.calc_liunian(user_bazi, req.year)
    result = {
        "birth_bazi": f"{user_bazi.year.gan}{user_bazi.year.zhi} {user_bazi.month.gan}{user_bazi.month.zhi} {user_bazi.day.gan}{user_bazi.day.zhi} {user_bazi.hour.gan}{user_bazi.hour.zhi}",
        "rizhu": f"{user_bazi.rizhu}({user_bazi.rizhu_wuxing})",
        "year": year_report.year,
        "year_ganzhi": year_report.year_ganzhi,
        "year_shengxiao": year_report.year_shengxiao,
        "nayin": year_report.nayin,
        "shishen": year_report.shishen_to_rizhu,
        "shishen_desc": year_report.shishen_desc,
        "chong": year_report.chong_pillars,
        "he": year_report.he_pillars,
        "xing": year_report.xing_pillars,
        "overall": year_report.overall,
        "career": year_report.career,
        "wealth": year_report.wealth,
        "health": year_report.health,
        "relationship": year_report.relationship,
    }

    # 流月
    if req.month:
        month_report = engine.calc_liumonth(user_bazi, req.year, req.month)
        result["liuyue"] = {
            "month": month_report.month,
            "month_ganzhi": month_report.month_ganzhi,
            "shishen": month_report.shishen_to_rizhu,
            "keywords": month_report.keywords,
        }

    return result


@app.post("/api/zeji")
def api_zeji(req: ZejiRequest):
    """择吉搜索：输入活动类型，返回未来合适的吉日"""
    from api.paipan.zeji import ZejiEngine, ACTIVITY_KEYWORDS

    engine = ZejiEngine()

    # 如果有用户八字，叠加个人分析
    user_bazi = None
    if req.birth_year:
        from api.paipan import paipan
        user_bazi = paipan(req.birth_year, req.birth_month or 1, req.birth_day or 1,
                           req.birth_hour, 0, req.gender)
        results = engine.search_with_personal(req.activity, user_bazi, req.days)
    else:
        results = engine.search(req.activity, req.days)

    return {
        "activity": req.activity,
        "keywords": ACTIVITY_KEYWORDS.get(req.activity, [req.activity]),
        "total": len(results),
        "dates": results,
    }


@app.post("/api/yongshen")
def api_yongshen(req: PaipanRequest):
    """用神推断"""
    from api.paipan import paipan
    from api.paipan.yongshen import YongshenEngine

    bazi = paipan(req.year, req.month, req.day, req.hour, req.minute, req.gender)
    engine = YongshenEngine()
    result = engine.analyze(bazi)

    return {
        "rizhu": result.rizhu,
        "rizhu_wuxing": result.rizhu_wuxing,
        "wangshuai": result.wangshuai,
        "wangshuai_reason": result.wangshuai_reason,
        "fuyi_yongshen": result.fuyi_yongshen,
        "tiaohou_yongshen": result.tiaohou_yongshen,
        "tongguan_yongshen": result.tongguan_yongshen,
        "recommended": result.recommended,
        "jishen": result.jishen,
        "analysis": result.analysis,
    }


@app.post("/api/qiming")
def api_qiming(req: QimingRequest):
    """八字起名"""
    from api.paipan import paipan
    from api.paipan.qiming import QimingEngine

    father = paipan(req.f_year, req.f_month, req.f_day, req.f_hour, 0, "男")
    mother = paipan(req.m_year, req.m_month, req.m_day, req.m_hour, 0, "女")

    engine = QimingEngine()
    result = engine.generate(father, mother, req.surname, req.gender)

    return {
        "surname": result.surname,
        "gender": result.gender,
        "father_rizhu": result.father_rizhu,
        "mother_rizhu": result.mother_rizhu,
        "father_yongshen": result.father_yongshen,
        "mother_yongshen": result.mother_yongshen,
        "recommended_wuxing": result.recommended_wuxing,
        "wuxing_reason": result.wuxing_reason,
        "suggestions": result.suggestions,
    }


@app.post("/api/zhouyi")
def api_zhouyi(req: ZhouyiRequest):
    """周易占卜"""
    from api.paipan.zhouyi import ZhouyiEngine

    engine = ZhouyiEngine()
    result = engine.divine(req.question)
    display = engine.get_hexagram_display(result.original_code)

    return {
        "question": result.question,
        "original_code": result.original_code,
        "original_name": result.original_name,
        "original_meaning": result.original_meaning,
        "original_advice": result.original_advice,
        "original_element": result.original_element,
        "direction": result.direction,
        "changing_lines": result.changing_lines,
        "changed_name": result.changed_name,
        "changed_meaning": result.changed_meaning,
        "analysis": result.analysis,
        "suggestion": result.suggestion,
        "display": display,
    }


@app.post("/api/geju")
def api_geju(req: PaipanRequest):
    """格局判定"""
    from api.paipan import paipan
    from api.paipan.geju import GejuEngine

    bazi = paipan(req.year, req.month, req.day, req.hour, req.minute, req.gender)
    engine = GejuEngine()
    result = engine.determine(bazi)

    return {
        "pattern": result.pattern,
        "pattern_type": result.pattern_type,
        "yueling": result.yueling,
        "yueling_shishen": result.yueling_shishen,
        "is_chengge": result.is_chengge,
        "chengge_conditions": result.chengge_conditions,
        "baige_reasons": result.baige_reasons,
        "analysis": result.analysis,
    }


@app.post("/api/fengshui")
def api_fengshui(req: FengshuiRequest):
    """阳宅风水分析"""
    from api.paipan.fengshui import FengshuiEngine, BAGUA_DIRECTIONS, XINGSHA_KB, QUEJIAO_IMPACT

    house = {
        "door_direction": req.door_direction,
        "kitchen": req.kitchen,
        "bedroom": req.bedroom,
        "bathroom": req.bathroom,
        "living_room": req.living_room,
        "missing_corners": req.missing_corners,
        "xingsha": req.xingsha,
    }

    engine = FengshuiEngine()
    report = engine.analyze(house)

    return {
        "house_gua": report.house_gua,
        "house_type": report.house_type,
        "four_ji": report.four_ji,
        "four_xiong": report.four_xiong,
        "jiugong_warnings": report.jiugong_warnings,
        "room_advice": report.room_advice,
        "xingsha_advice": report.xingsha_advice,
        "quejiao_advice": report.quejiao_advice,
        "summary": report.summary,
        # 返回可选值供前端下拉
        "options": {
            "directions": list(BAGUA_DIRECTIONS.keys()),
            "xingsha_types": list(XINGSHA_KB.keys()),
            "quejiao_types": list(QUEJIAO_IMPACT.keys()),
        },
    }


@app.post("/api/hehun")
def api_hehun(req: HehunRequest):
    """八字合婚"""
    from api.paipan import paipan
    from api.paipan.hehun import HehunEngine

    male = paipan(req.m_year, req.m_month, req.m_day, req.m_hour, req.m_minute, "男")
    female = paipan(req.f_year, req.f_month, req.f_day, req.f_hour, req.f_minute, "女")

    engine = HehunEngine()
    report = engine.analyze(male, female)

    return {
        "male_bazi": report.male_bazi,
        "female_bazi": report.female_bazi,
        "male_rizhu": report.male_rizhu,
        "female_rizhu": report.female_rizhu,
        "nianzhu_score": report.nianzhu_score,
        "nianzhu_detail": report.nianzhu_detail,
        "rizhi_score": report.rizhi_score,
        "rizhi_detail": report.rizhi_detail,
        "wuxing_score": report.wuxing_score,
        "wuxing_detail": report.wuxing_detail,
        "shishen_score": report.shishen_score,
        "shishen_detail": report.shishen_detail,
        "total_score": report.total_score,
        "level": report.level,
        "summary": report.summary,
    }


@app.get("/api/xuetang")
def api_xuetang():
    """获取学堂教材章节列表"""
    import json
    from pathlib import Path

    chapters_file = Path(__file__).parent.parent / "data" / "learning_chapters.json"
    if not chapters_file.exists():
        return {"chapters": []}

    with open(chapters_file, encoding="utf-8") as f:
        data = json.load(f)

    # 只返回章节摘要，不返回完整教材内容（内容按需获取）
    chapters_summary = []
    for ch in data["chapters"]:
        chapters_summary.append({
            "id": ch["id"],
            "title": ch["title"],
            "subtitle": ch["subtitle"],
            "order": ch["order"],
            "unlock_requires": ch.get("unlock_requires"),
            "question_count": len(ch.get("quiz_ids", [])),
            "pass_score": ch.get("pass_score", 7),
        })

    return {
        "course": data["course"],
        "chapters": chapters_summary,
    }


@app.get("/api/xuetang/{chapter_id}")
def api_xuetang_chapter(chapter_id: str):
    """获取单章教材完整内容（含课文+测验题目）"""
    import json
    from pathlib import Path

    chapters_file = Path(__file__).parent.parent / "data" / "learning_chapters.json"
    quiz_file = Path(__file__).parent.parent / "data" / "quiz_cases.jsonl"

    with open(chapters_file, encoding="utf-8") as f:
        data = json.load(f)

    chapter = None
    for ch in data["chapters"]:
        if ch["id"] == chapter_id:
            chapter = ch
            break

    if not chapter:
        return {"error": "章节未找到"}

    # 加载关联的测验题
    questions = []
    if quiz_file.exists():
        with open(quiz_file, encoding="utf-8") as f:
            all_quizzes = [json.loads(l) for l in f if l.strip()]
        quiz_ids = set(chapter.get("quiz_ids", []))
        for q in all_quizzes:
            if q["id"] in quiz_ids:
                questions.append({
                    "id": q["id"],
                    "title": q["title"],
                    "difficulty": q["difficulty"],
                    "story": q["story"],
                    "question": q["question"],
                    "options": q["options"],
                })

    return {
        "id": chapter["id"],
        "title": chapter["title"],
        "subtitle": chapter["subtitle"],
        "order": chapter["order"],
        "unlock_requires": chapter.get("unlock_requires"),
        "pass_score": chapter.get("pass_score", 7),
        "content": chapter["content"],
        "questions": questions,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
