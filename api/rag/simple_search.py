"""
零依赖关键词搜索（保底方案）
===========================
不依赖任何ML库，纯Python实现。
即使 onnxruntime/chromadb 装不上也能用。

用法:
  from api.rag.simple_search import SimpleSearcher
  s = SimpleSearcher()
  results = s.search("正官格", top_k=5)
"""

import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data" / "cleaned"


class SimpleSearcher:
    """基于TF-IDF关键词匹配的轻量检索器"""

    def __init__(self):
        self._records = None
        self._index = None  # word -> [record_indices]

    def _load(self):
        """加载所有记录并建索引"""
        if self._records is not None:
            return

        print("加载古籍数据...")
        self._records = []
        self._index = {}

        for fpath in sorted(DATA_DIR.glob("*.json")):
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            for rec in data["records"]:
                text = rec.get("original", "")
                if len(text) < 30:
                    continue
                idx = len(self._records)
                self._records.append(rec)

                # 建立词索引（2-4字词组）
                words = set()
                for n in [2, 3, 4]:
                    for i in range(len(text) - n + 1):
                        words.add(text[i:i + n])

                for w in words:
                    if w not in self._index:
                        self._index[w] = []
                    self._index[w].append(idx)

        print(f"  加载 {len(self._records)} 条记录, {len(self._index)} 个索引词")

    def search(self, query: str, top_k: int = 5, filter_source: str = None) -> list[dict]:
        """搜索"""
        self._load()

        # 提取查询中的关键词（2-4字）
        query_words = set()
        for n in [2, 3, 4]:
            for i in range(len(query) - n + 1):
                query_words.add(query[i:i + n])

        # 统计每条记录的命中次数
        scores = Counter()
        for w in query_words:
            if w in self._index:
                for idx in self._index[w]:
                    scores[idx] += 1

        # 按分数排序
        results = []
        for idx, score in scores.most_common(top_k * 3):
            rec = self._records[idx]
            if filter_source and rec["source_name"] != filter_source:
                continue
            results.append({
                "content": rec["original"][:500],
                "source_name": rec["source_name"],
                "volume": rec.get("volume", ""),
                "section": rec.get("section", ""),
                "tags": rec.get("tags", []),
                "score": min(1.0, score / max(len(query_words), 1)),
            })
            if len(results) >= top_k:
                break

        return results

    def search_for_ai(self, query: str, top_k: int = 3) -> str:
        """为AI准备上下文"""
        results = self.search(query, top_k=top_k)
        if not results:
            return "经籍未载相关内容，不敢妄断。"

        parts = []
        for i, r in enumerate(results):
            parts.append(
                f"【引用{i + 1}】《{r['source_name']}》{r['volume']}·{r['section']}\n"
                f"{r['content']}\n"
                f"(匹配度: {r['score']:.0%})"
            )
        return "\n\n".join(parts)
