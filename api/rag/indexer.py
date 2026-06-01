"""
古籍文本向量化索引器
====================
将Layer 1的结构化JSON文本向量化并存入ChromaDB。

默认使用 ChromaDB 内置 ONNX 嵌入 (all-MiniLM-L6-v2, 轻量)
可选使用 sentence-transformers (BGE-M3, 需PyTorch)

用法:
  python -m api.rag.indexer
  python -m api.rag.indexer --rebuild  # 重建索引
  python -m api.rag.indexer --sample 100  # 只索引前100条(测试用)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data" / "cleaned"
CHROMA_DIR = ROOT / "data" / "chroma_db"

# 配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
BATCH_SIZE = 50


class TextIndexer:
    """文本向量化索引器 (使用 ChromaDB 内置嵌入)"""

    def __init__(self, use_bge: bool = False):
        self.use_bge = use_bge
        self._embedding_fn = None
        self._client = None
        self._collection = None

    @property
    def embedding_fn(self):
        """获取嵌入函数"""
        if self._embedding_fn is None:
            if self.use_bge:
                from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
                self._embedding_fn = SentenceTransformerEmbeddingFunction(
                    model_name="BAAI/bge-small-zh-v1.5"
                )
            else:
                # 使用 ONNX 运行时，无需 PyTorch
                from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
                self._embedding_fn = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
                print("  使用内置ONNX嵌入 (all-MiniLM-L6-v2, CPU)")
        return self._embedding_fn

    @property
    def collection(self):
        """获取ChromaDB集合"""
        if self._collection is None:
            import chromadb
            from chromadb.config import Settings

            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name="ancient_texts",
                metadata={"description": "命理古籍原文向量库"},
            )
        return self._collection

    def load_records(self, limit: int = 0) -> list[dict]:
        """加载清洗后的JSON记录"""
        all_records = []
        for fpath in sorted(DATA_DIR.glob("*.json")):
            print(f"  加载: {fpath.name}")
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            records = data["records"]
            records = [r for r in records if len(r.get("original", "")) > 30]
            all_records.extend(records)
            if limit and len(all_records) >= limit:
                all_records = all_records[:limit]
                break
            print(f"    {len(records)} 条有效")

        print(f"  总计: {len(all_records)} 条记录")
        return all_records

    def chunk_text(self, text: str) -> list[str]:
        """将长文本分割为重叠块"""
        if len(text) <= CHUNK_SIZE:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            if end < len(text):
                for sep in ["\n", "。", "；", "，"]:
                    pos = text.rfind(sep, start, end)
                    if pos > start + CHUNK_SIZE // 2:
                        end = pos + 1
                        break

            chunk = text[start:end].strip()
            if chunk and len(chunk) > 20:
                chunks.append(chunk)
            start = end - CHUNK_OVERLAP
        return chunks

    def build_index(self, rebuild: bool = False, sample_limit: int = 0):
        """构建向量索引"""
        print("1. 加载结构化数据...")
        records = self.load_records(limit=sample_limit)

        print("\n2. 文本分块...")
        chunks, chunk_meta = [], []
        for rec in records:
            texts = self.chunk_text(rec["original"])
            for j, chunk in enumerate(texts):
                chunks.append(chunk)
                chunk_meta.append({
                    "record_id": rec["id"],
                    "source_name": rec["source_name"],
                    "volume": rec.get("volume", ""),
                    "section": rec.get("section", ""),
                    "tags": ",".join(rec.get("tags", [])),
                })
        avg_len = sum(len(c) for c in chunks) // max(len(chunks), 1)
        print(f"  {len(chunks)} 块 (均{avg_len}字)")

        if rebuild:
            print("\n3. 清除旧索引...")
            try:
                self._client.delete_collection("ancient_texts")
            except Exception:
                pass
            self._collection = None
        else:
            print("\n3. 跳过清除 (追加模式)")

        print(f"\n4. 向量化并写入ChromaDB ({len(chunks)}块)...")
        col = self.collection
        ef = self.embedding_fn  # 触发模型加载

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            metas = chunk_meta[i:i + BATCH_SIZE]
            ids = [f"chunk_{j:06d}" for j in range(i, i + len(batch))]

            col.add(ids=ids, documents=batch, metadatas=metas)

            if (i // BATCH_SIZE) % 20 == 0:
                pct = min(100, i * 100 // len(chunks))
                print(f"  {i}/{len(chunks)} ({pct}%) ...")

        print(f"  完成! 索引总量: {col.count()}")

        # 保存统计
        stats = {
            "total_chunks": len(chunks),
            "total_records": len(records),
            "avg_chunk_len": avg_len,
            "embedding": "ONNX-all-MiniLM-L6-v2" if not self.use_bge else "BGE-small-zh-v1.5",
        }
        with open(CHROMA_DIR / "index_stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"\n索引完成: {json.dumps(stats, ensure_ascii=False)}")
        return stats


def main():
    rebuild = "--rebuild" in sys.argv
    use_bge = "--bge" in sys.argv
    sample = 0
    if "--sample" in sys.argv:
        idx = sys.argv.index("--sample")
        sample = int(sys.argv[idx + 1])

    indexer = TextIndexer(use_bge=use_bge)
    indexer.build_index(rebuild=rebuild, sample_limit=sample)


if __name__ == "__main__":
    main()
