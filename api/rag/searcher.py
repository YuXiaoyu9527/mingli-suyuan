"""
RAG检索器
=========
基于ChromaDB向量搜索的古籍段落检索。

用法:
  from api.rag.searcher import RAGSearcher
  searcher = RAGSearcher()
  results = searcher.search("正官格是什么意思", top_k=5)
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CHROMA_DIR = ROOT / "data" / "chroma_db"


class RAGSearcher:
    """古籍RAG检索器"""

    def __init__(self):
        self._ef = None
        self._collection = None

    def ensure_ready(self):
        if self._collection is not None:
            return

        import chromadb
        from chromadb.config import Settings
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        print("初始化RAG检索器...")
        self._ef = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])

        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = client.get_collection("ancient_texts")
        print(f"  索引就绪: {self._collection.count()} 条")

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_source: str = None,
    ) -> list[dict]:
        """检索与查询最相关的古籍段落"""
        self.ensure_ready()

        where = None
        if filter_source:
            where = {"source_name": filter_source}

        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        formatted = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i]
                score = max(0.0, min(1.0, 1.0 - dist / 2.0))

                formatted.append({
                    "content": results["documents"][0][i],
                    "source_name": meta.get("source_name", ""),
                    "volume": meta.get("volume", ""),
                    "section": meta.get("section", ""),
                    "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
                    "record_id": meta.get("record_id", ""),
                    "score": round(score, 4),
                })
        return formatted

    def search_for_ai(self, query: str, top_k: int = 3) -> str:
        """为AI解读准备格式化的上下文"""
        results = self.search(query, top_k=top_k)
        if not results:
            return "经籍未载相关内容，不敢妄断。"

        parts = []
        for i, r in enumerate(results):
            parts.append(
                f"【引用{i+1}】《{r['source_name']}》{r['volume']}·{r['section']}\n"
                f"{r['content']}\n"
                f"(相关度: {r['score']:.0%})"
            )
        return "\n\n".join(parts)
