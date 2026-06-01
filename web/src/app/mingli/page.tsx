"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import { searchAncient } from "@/lib/api";
import { Search, Star, Loader2 } from "lucide-react";

export default function MingliPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await searchAncient(query, 10);
      setResults(data.results || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          古籍检索
        </h1>
        <p className="text-aged text-sm mt-1">
          搜索4,879条古籍原文 · 四库全书底本
        </p>
      </header>

      {/* 搜索栏 */}
      <div className="px-5 mb-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-aged" />
            <input type="text" value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="输入关键词：格局/神煞/干支/人名…"
              className="w-full bg-parchment-dark border border-parchment-darker rounded-lg pl-10 pr-4 py-2.5 text-ink text-sm focus:outline-none focus:border-gold" />
          </div>
          <button onClick={handleSearch} disabled={loading}
            className="bg-vermillion text-white px-4 rounded-lg tap-active">
            {loading ? <Loader2 size={18} className="animate-spin" /> : "搜索"}
          </button>
        </div>
      </div>

      {/* 结果列表 */}
      <div className="px-5 flex-1 space-y-3">
        {results.map((r, i) => (
          <div key={i} className="card-ancient">
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="text-xs font-bold text-vermillion font-[family-name:var(--font-display)]">
                  {r.source_name}
                </span>
                <span className="text-[11px] text-aged ml-2">{r.volume} · {r.section}</span>
              </div>
              <span className="text-[11px] text-gold">{Math.round(r.score * 100)}%</span>
            </div>
            <p className="text-sm text-ink-light leading-relaxed line-clamp-4">{r.content}</p>
            <div className="flex gap-1.5 mt-2">
              {(r.tags || []).filter((t:string) => t !== "其他").slice(0, 4).map((t:string) => (
                <span key={t} className="text-[10px] px-1.5 py-0.5 bg-gold/10 text-aged rounded">{t}</span>
              ))}
            </div>
          </div>
        ))}

        {results.length === 0 && !loading && query && (
          <p className="text-center text-aged text-sm py-8">未找到匹配的古籍段落。试试其他关键词？</p>
        )}

        {results.length === 0 && !loading && !query && (
          <div className="text-center text-aged text-sm py-8 space-y-2">
            <p>🔍 试试搜索：</p>
            <div className="flex flex-wrap justify-center gap-2">
              {["正官格", "五行相生", "天乙贵人", "嫁娶吉日", "桃花煞"].map(t => (
                <button key={t} onClick={() => { setQuery(t); handleSearch(); }}
                  className="px-3 py-1 bg-parchment-dark rounded-full text-xs text-ink-light tap-active border border-parchment-darker">
                  {t}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
