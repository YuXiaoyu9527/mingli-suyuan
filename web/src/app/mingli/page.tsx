"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { getMingli } from "@/lib/api";
import { Search, Star, Loader2, FilterX } from "lucide-react";

export default function MingliPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [patternFilter, setPatternFilter] = useState("");
  const [selectedCase, setSelectedCase] = useState<any>(null);

  const loadCases = async (p?: string, s?: string) => {
    setLoading(true);
    try {
      const data = await getMingli(p || undefined, s || undefined);
      setCases(data.cases || []);
      setPatterns(data.patterns || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { loadCases(); }, []);

  const handleSearch = () => {
    loadCases(patternFilter, search);
  };

  const clearFilters = () => {
    setSearch("");
    setPatternFilter("");
    loadCases();
  };

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-dao-ink font-[family-name:var(--font-display)] tracking-wider">
          历史命例
        </h1>
        <p className="text-dao-aged text-sm mt-1">
          {total}位历史人物 · 格局溯源 · 验案考据
        </p>
      </header>

      {/* 搜索栏 */}
      <div className="px-5 mb-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-dao-aged" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="搜索人名、格局、干支…"
              className="w-full bg-dao-paper-dark border border-dao-paper-darker rounded-lg
                         pl-9 pr-3 py-2 text-dao-ink text-sm
                         focus:outline-none focus:border-dao-gold placeholder:text-dao-aged-light" />
          </div>
          <button onClick={handleSearch} disabled={loading}
            className="bg-dao-red text-white px-3 rounded-lg tap-active text-xs">
            {loading ? <Loader2 size={16} className="animate-spin" /> : "搜索"}
          </button>
        </div>
      </div>

      {/* 格局筛选瓷片 */}
      <div className="px-5 mb-4">
        <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
          <button onClick={clearFilters}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs border transition-colors tap-active
              ${!patternFilter ? "bg-dao-red text-white border-dao-red" : "bg-dao-paper-dark text-dao-ink-light border-dao-paper-darker"}`}>
            全部({total})
          </button>
          {patterns.slice(0, 8).map(({ name, count }) => (
            <button key={name}
              onClick={() => { setPatternFilter(name); loadCases(name, search); }}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs border transition-colors tap-active
                ${patternFilter === name ? "bg-dao-gold/20 text-dao-gold-dark border-dao-gold/50"
                                              : "bg-dao-paper-dark text-dao-ink-light border-dao-paper-darker"}`}>
              {name}({count})
            </button>
          ))}
        </div>
      </div>

      {/* 命例卡片列表 */}
      <div className="px-5 flex-1 space-y-3">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={28} className="animate-spin text-dao-gold" />
          </div>
        )}

        {!loading && cases.length === 0 && (
          <p className="text-center text-dao-aged text-sm py-12">无匹配命例</p>
        )}

        {cases.map((mingli) => (
          <div key={mingli.id} className="dao-card tap-active"
            onClick={() => setSelectedCase(mingli)}>
            {/* 姓名 + 格局 + 可信度 */}
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="text-base font-bold text-dao-ink font-[family-name:var(--font-display)]">
                  {mingli.name}
                </h3>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-dao-aged">{mingli.era}</span>
                  <span className="text-xs font-mono text-dao-ink-light">{mingli.bazi}</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="px-2 py-0.5 bg-dao-red/10 text-dao-red text-[10px]
                                rounded-full border border-dao-red/20">
                  {mingli.pattern}
                </span>
                <span className="flex items-center gap-1 text-[10px] text-dao-aged">
                  <Star size={9} className={`${mingli.reliability === "正史记载" ? "fill-dao-gold text-dao-gold" : "text-dao-aged-light"}`} />
                  {mingli.reliability}
                </span>
              </div>
            </div>

            {/* 日主 */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] text-dao-aged">日主</span>
              <span className="text-sm font-bold text-dao-red font-[family-name:var(--font-display)]">
                {mingli.rishu}
              </span>
            </div>

            {/* 断语 */}
            <p className="text-xs text-dao-ink-light leading-relaxed line-clamp-3">
              {mingli.commentary}
            </p>

            {/* 出处 + 标签 */}
            <div className="flex items-center justify-between mt-2">
              <span className="text-[10px] text-dao-aged-light">
                {mingli.source}
              </span>
              <div className="flex gap-1">
                {(mingli.tags || []).slice(0, 3).map((t: string) => (
                  <span key={t} className="text-[9px] px-1.5 py-0.5 bg-dao-paper-dark text-dao-aged rounded">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 详情弹窗 */}
      {selectedCase && (
        <div className="fixed inset-0 z-[60] flex items-end justify-center bg-dao-ink/40 backdrop-blur-sm"
          onClick={() => setSelectedCase(null)}>
          <div className="w-full max-w-[430px] bg-dao-paper rounded-t-2xl p-6 max-h-[70vh] overflow-y-auto anim-enter"
            onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-[family-name:var(--font-display)] text-dao-ink">
                  {selectedCase.name}
                </h2>
                <p className="text-xs text-dao-aged">{selectedCase.era} · {selectedCase.pattern} · {selectedCase.rishu}日主</p>
              </div>
              <button onClick={() => setSelectedCase(null)}
                className="text-dao-aged text-xl">&times;</button>
            </div>

            {/* 八字柱式 */}
            <div className="grid grid-cols-4 gap-2 text-center mb-4">
              {selectedCase.bazi.split(" ").map((gz: string, i: number) => {
                const labels = ["年柱", "月柱", "日柱", "时柱"];
                return (
                  <div key={i} className="pillar-block py-2">
                    <p className="text-[9px] text-dao-aged">{labels[i]}</p>
                    <p className="text-base font-[family-name:var(--font-display)] text-dao-ink">{gz[0]}</p>
                    <p className="text-base font-[family-name:var(--font-display)] text-dao-red">{gz[1]}</p>
                  </div>
                );
              })}
            </div>

            {/* 断语 */}
            <div className="classical-quote text-sm mb-3">
              {selectedCase.commentary}
            </div>

            <div className="flex items-center gap-4 text-xs text-dao-aged mb-2">
              <span>来源: {selectedCase.source}</span>
              <span className="flex items-center gap-1">
                <Star size={10} className={selectedCase.reliability === "正史记载" ? "fill-dao-gold text-dao-gold" : ""} />
                {selectedCase.reliability}
              </span>
            </div>

            <div className="flex flex-wrap gap-1">
              {(selectedCase.tags || []).map((t: string) => (
                <span key={t} className="px-2 py-0.5 bg-dao-paper-dark text-dao-aged text-[10px] rounded-full">
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      <BottomNav />
    </div>
  );
}
