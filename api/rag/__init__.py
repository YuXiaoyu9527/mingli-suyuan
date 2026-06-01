"""
RAG检索层 - 古籍原文向量检索

用法:
  from api.rag import RAGSearcher
  searcher = RAGSearcher()
  results = searcher.search("正官格", top_k=5)
"""

from .searcher import RAGSearcher
from .indexer import TextIndexer

__all__ = ["RAGSearcher", "TextIndexer"]
