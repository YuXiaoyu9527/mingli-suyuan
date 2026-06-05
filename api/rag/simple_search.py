"""
零依赖关键词搜索（保底方案 + 低内存优化）
==========================================
不依赖任何ML库，纯Python实现。
即使 onnxruntime/chromadb 装不上也能用。

🔧 2024.06 低内存优化：
  - 去掉 n-gram 预索引（原方案内存占用 ~700MB+，笔记本直接卡死）
  - 改为流式扫描 + 关键词匹配，内存稳定在 ~10MB
  - 4800条记录扫描耗时 <100ms，完全可以接受

用法:
  from api.rag.simple_search import SimpleSearcher
  s = SimpleSearcher()
  results = s.search("正官格", top_k=5)
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data" / "cleaned"


class SimpleSearcher:
    """
    基于关键词匹配的轻量检索器。

    内存策略（v2）：
    - 只加载记录的 text+metadata，不建 n-gram 索引
    - 搜索时 O(n) 扫描，用集合运算做关键词匹配
    - 预估内存：4800条 × 平均400字 ≈ 2MB 文本 + 少量元数据 ≈ 5-10MB 总量
    - 对比旧版 n-gram 索引：660万个key → 700MB+，降低约 99% 内存
    """

    def __init__(self):
        self._records: list | None = None  # 延迟加载

    def _load(self):
        """加载所有记录（只存文本，不建索引）"""
        if self._records is not None:
            return

        self._records = []
        for fpath in sorted(DATA_DIR.glob("*.json")):
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            for rec in data["records"]:
                text = rec.get("original", "")
                if len(text) < 30:
                    continue
                self._records.append({
                    "content": text,
                    "source_name": rec.get("source_name", ""),
                    "volume": rec.get("volume", ""),
                    "section": rec.get("section", ""),
                    "tags": rec.get("tags", []),
                    "record_id": rec.get("id", ""),
                })

        # 只在首次加载时打印
        if self._records:
            print(f"  [SimpleSearcher v2] 加载 {len(self._records)} 条记录 (~{sum(len(r['content']) for r in self._records) // 1000}K 字符), 内存安全")

    def _extract_keywords(self, text: str) -> set[str]:
        """
        从查询文本中提取关键词。

        中文没有空格分词，用以下策略：
        1. 提取2-4字的连续中文子串（限制数量防止爆炸）
        2. 保留原始查询（精确匹配）
        """
        keywords = set()
        # 只取纯中文部分
        chinese_chars = re.sub(r'[^一-鿿]', '', text)

        # 限制关键词生成数量：只取前300个字符的n-gram
        limited = chinese_chars[:300]
        for n in [2, 3, 4]:
            for i in range(len(limited) - n + 1):
                keywords.add(limited[i:i + n])

        # 原始查询作为整体关键词
        keywords.add(text.strip())
        return keywords

    def search(self, query: str, top_k: int = 5, filter_source: str = None) -> list[dict]:
        """
        搜索。

        复杂度：O(N × K)，N=记录数(~4800)，K=关键词数(~300)
        在普通笔记本上 <100ms
        """
        self._load()
        if not self._records:
            return []

        keywords = self._extract_keywords(query)

        # 对每条记录打分
        scored = []
        for rec in self._records:
            if filter_source and rec["source_name"] != filter_source:
                continue

            score = 0
            content = rec["content"]
            # 关键词命中计数
            for kw in keywords:
                if kw in content:
                    score += 1
            # 标题/章节命中加权
            if query.strip() in rec.get("section", ""):
                score += 3
            if query.strip() in rec.get("volume", ""):
                score += 2
            # 标签命中加权
            for tag in rec.get("tags", []):
                if query.strip() in tag:
                    score += 2

            if score > 0:
                scored.append((score, rec))

        # 按分数降序排列
        scored.sort(key=lambda x: -x[0])

        # 格式化结果
        max_score = max((s for s, _ in scored), default=1)
        results = []
        for score, rec in scored[:top_k]:
            results.append({
                "content": rec["content"][:500],
                "source_name": rec["source_name"],
                "volume": rec["volume"],
                "section": rec["section"],
                "tags": rec["tags"],
                "score": round(min(1.0, score / max(max_score, 1)), 4),
            })

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

    @property
    def record_count(self) -> int:
        """返回已加载记录数（不触发加载）"""
        return len(self._records) if self._records else 0