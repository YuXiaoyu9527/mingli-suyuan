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
        # 优先用向量搜索，装不上用关键词搜索
        try:
            from api.rag import RAGSearcher
            _searcher = RAGSearcher()
        except Exception:
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
    result = paipan(req.year, req.month, req.day, req.hour, req.minute, req.gender)
    return to_dict(result)


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
    今日宜忌（建除十二神 + 黄道黑道 + 彭祖百忌 + 个人冲合）

    如果不传用户八字参数，只返回通用宜忌。
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
    result = yj.analyze(solar, user_bazi)

    return {
        "date": result.date,
        "day_ganzhi": result.day_ganzhi,
        "jianchu": result.jianchu,
        "jianchu_desc": result.jianchu_desc,
        "huangdao_shen": result.huangdao_shen,
        "huangdao_type": result.huangdao_type,
        "pengzu_ji": result.pengzu_ji,
        "general_yi": result.general_yi,
        "general_ji": result.general_ji,
        "personal_yi": result.personal_yi,
        "personal_ji": result.personal_ji,
        "personal_analysis": result.personal_analysis,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
