"""
命理溯源 - 统一API服务
======================
FastAPI服务器，整合排盘引擎 + RAG检索 + AI解读。

启动:
  uvicorn api.server:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="命理溯源 API",
    description="八字排盘 + 古籍RAG检索 + AI解读",
    version="0.1.0",
)

# CORS (允许前端跨域访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 请求/响应模型 =====

class PaipanRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    gender: str = "男"
    tz: int = 8


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source: Optional[str] = None


# ===== 懒加载单例 =====

_searcher = None


def get_searcher():
    global _searcher
    if _searcher is None:
        from api.rag import RAGSearcher
        _searcher = RAGSearcher()
    return _searcher


# ===== API端点 =====

@app.get("/")
def root():
    return {"name": "命理溯源 API", "version": "0.1.0", "status": "ok"}


@app.post("/api/paipan")
def api_paipan(req: PaipanRequest):
    """八字排盘"""
    from api.paipan import paipan, to_dict
    result = paipan(req.year, req.month, req.day, req.hour, req.minute, req.gender, req.tz)
    return to_dict(result)


@app.post("/api/search")
def api_search(req: SearchRequest):
    """古籍原文检索"""
    searcher = get_searcher()
    results = searcher.search(
        req.query,
        top_k=req.top_k,
        filter_source=req.source,
    )
    return {
        "query": req.query,
        "total": len(results),
        "results": results,
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


@app.get("/health")
def health():
    return {"status": "healthy"}
