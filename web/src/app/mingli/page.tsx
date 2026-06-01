"use client";

import BottomNav from "@/components/BottomNav";
import { Users, Search, Star } from "lucide-react";
import { useState } from "react";

// 示例命例数据
const sampleCases = [
  {
    id: 1,
    name: "李鸿章",
    bazi: "癸未 甲寅 乙亥 己卯",
    pattern: "正官格",
    rizhu: "乙木",
    reliability: "正史记载",
    excerpt: "乙木春生，得癸水滋润，甲木帮扶，官星得位，故能出将入相。然木盛土虚，晚年脾胃有疾……",
    source: "《滴天髓阐微》",
  },
  {
    id: 2,
    name: "曾国藩",
    bazi: "辛未 己亥 丙辰 己亥",
    pattern: "七杀格",
    rizhu: "丙火",
    reliability: "正史记载",
    excerpt: "丙火生亥月，水旺火弱，七杀当令。然辛金透干化杀，己土制水，格局清奇……",
    source: "《滴天髓阐微》",
  },
  {
    id: 3,
    name: "朱元璋",
    bazi: "戊辰 壬戌 丁丑 丁未",
    pattern: "伤官格",
    rizhu: "丁火",
    reliability: "后人推定",
    excerpt: "丁火生戌月，伤官吐秀。戊土透干，壬水相济，火土金水四行俱全，格局奇特……",
    source: "《三命通会》",
  },
];

export default function MingliPage() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* 顶部 */}
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          历史命例
        </h1>
        <p className="text-aged text-sm mt-1">
          古人八字 · 格局溯源 · 验案考据
        </p>
      </header>

      {/* 搜索栏 */}
      <div className="px-5 mb-4">
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-aged"
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索格局、人名、干支……"
            className="w-full bg-parchment-dark border border-parchment-darker
                       rounded-lg pl-10 pr-4 py-2.5 text-ink text-sm
                       focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/20
                       transition-all placeholder:text-aged-light"
          />
        </div>
      </div>

      {/* 标签筛选 */}
      <div className="px-5 mb-4">
        <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
          {["全部", "正官格", "七杀格", "建禄格", "伤官格", "食神格"].map(
            (tag) => (
              <button
                key={tag}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs
                           border transition-colors tap-active
                           ${tag === "全部"
                             ? "bg-vermillion text-white border-vermillion"
                             : "bg-parchment-dark text-ink-light border-parchment-darker hover:border-gold/50"
                           }`}
              >
                {tag}
              </button>
            )
          )}
        </div>
      </div>

      {/* 命例卡片列表 */}
      <div className="px-5 flex-1 space-y-4">
        {sampleCases.map((mingli) => (
          <div key={mingli.id} className="card-ancient tap-active">
            {/* 头部：姓名 + 格局 + 可信度 */}
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-base font-bold text-ink font-[family-name:var(--font-display)]">
                  {mingli.name}
                </h3>
                <p className="text-sm text-ink-light font-mono mt-0.5">
                  {mingli.bazi}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <span className="inline-block px-2 py-0.5 bg-vermillion/10 text-vermillion
                                text-[11px] rounded-full border border-vermillion/20">
                  {mingli.pattern}
                </span>
                <span className="flex items-center gap-1 text-[11px] text-aged">
                  <Star size={10} className="fill-gold text-gold" />
                  {mingli.reliability}
                </span>
              </div>
            </div>

            {/* 古籍断语 */}
            <div className="classical-quote text-sm mb-2">
              {mingli.excerpt}
            </div>

            {/* 出处 + 详情链接 */}
            <div className="flex items-center justify-between mt-2">
              <span className="text-[11px] text-aged-light">
                📖 出自{mingli.source}
              </span>
              <button className="text-xs text-indigo-traditional tap-active font-medium
                                 hover:text-indigo-light transition-colors">
                查看详情 →
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 提示 */}
      <div className="px-5 pb-2">
        <p className="text-center text-[11px] text-aged-light">
          当前收录 {sampleCases.length} 例 · 更多命例即将上线
        </p>
      </div>

      <BottomNav />
    </div>
  );
}
