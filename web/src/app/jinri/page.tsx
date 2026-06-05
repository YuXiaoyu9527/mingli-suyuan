"use client";

import { useState, useEffect } from "react";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import Link from "next/link";

export default function JinriPage() {
  const [yiji, setYiji] = useState<any>(null);
  const [ancient, setAncient] = useState<any>(null);
  const [mingli, setMingli] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadToday();
  }, []);

  const loadToday = async () => {
    setLoading(true);
    try {
      const [yResp, aResp, mResp] = await Promise.all([
        fetch(`${getApiUrl()}/api/yiji`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }),
        fetch(`${getApiUrl()}/api/search`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: "五行", top_k: 1 }),
        }),
        fetch(`${getApiUrl()}/api/mingli`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }),
      ]);
      setYiji(await yResp.json());
      const aData = await aResp.json();
      setAncient(aData.results?.[0] || null);
      const mData = await mResp.json();
      const cases = mData.cases || [];
      setMingli(cases[Math.floor(Math.random() * cases.length)] || null);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const quickLinks = [
    { icon: "☯", label: "排盘", href: "/paipan" },
    { icon: "🔮", label: "占卜", href: "/zhouyi" },
    { icon: "🏠", label: "风水", href: "/fengshui" },
    { icon: "📖", label: "典籍", href: "/dianji" },
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* Calendar Hero */}
      <header className="px-5 pt-8 pb-2 text-center anim-page-enter">
        {yiji && (
          <>
            <p className="text-xs text-text-secondary tracking-[0.2em]">
              甲辰年 · {yiji.lunar_date?.replace(/年|月/g, (m: string) => (m === "年" ? " · " : " · ")) || ""}
            </p>
            <h1
              className="text-[52px] font-[family-name:var(--font-display)] text-text leading-none mt-2"
              style={{ animation: "countUp 0.6s 0.2s cubic-bezier(0.22,1,0.36,1) both" }}
            >
              {yiji.day_ganzhi?.[0] || "——"}
            </h1>
            <p
              className="text-sm text-text-secondary tracking-wider mt-1"
              style={{ animation: "countUp 0.6s 0.4s cubic-bezier(0.22,1,0.36,1) both" }}
            >
              {yiji.week || ""} · {yiji.day_ganzhi || ""}日 · {yiji.shengxiao || ""}
            </p>
          </>
        )}
      </header>

      <div className="px-5 flex-1 space-y-4 anim-stagger-8">
        {/* 宜忌卡片 */}
        {yiji && (
          <div className="dao-card flex divide-x divide-border">
            <div className="flex-1 text-center py-3">
              <p className="text-[10px] text-accent tracking-[0.15em] mb-2">宜</p>
              <p className="text-sm text-text leading-relaxed">
                {(yiji.yi || []).slice(0, 5).join(" · ")}
              </p>
            </div>
            <div className="flex-1 text-center py-3">
              <p className="text-[10px] text-text-secondary tracking-[0.15em] mb-2">忌</p>
              <p className="text-sm text-accent/70 leading-relaxed">
                {(yiji.ji || []).slice(0, 5).join(" · ")}
              </p>
            </div>
          </div>
        )}

        {/* 冲煞 */}
        {yiji?.chong_desc && (
          <p className="text-center text-xs text-text-tertiary">
            {yiji.chong_shengxiao ? `冲${yiji.chong_shengxiao}` : ""}
            {yiji.sha_direction ? ` · 煞${yiji.sha_direction}` : ""}
          </p>
        )}

        {/* 四宫格 */}
        <div className="grid grid-cols-4 gap-3">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="dao-card flex flex-col items-center gap-1.5 py-4 tap-active hover:border-gold/40 transition-colors"
            >
              <span className="text-2xl">{link.icon}</span>
              <span className="text-xs text-text">{link.label}</span>
            </Link>
          ))}
        </div>

        {/* 每日古籍 */}
        {ancient && (
          <Link
            href={`/xuetang?from=jinri&ref=${encodeURIComponent(ancient.section || ancient.source_name || "")}`}
            className="block dao-card-warm tap-active hover:shadow-md transition-shadow"
          >
            <p className="text-[10px] text-gold tracking-[0.1em] mb-2">📖 每日古籍</p>
            <p className="text-sm text-text leading-relaxed line-clamp-3">{ancient.content}</p>
            <p className="text-[11px] text-text-tertiary mt-2">
              ——《{ancient.source_name}》{ancient.volume}
            </p>
          </Link>
        )}

        {/* 历史命例 */}
        {mingli && (
          <div className="dao-card tap-active">
            <p className="text-[10px] text-accent tracking-[0.1em] mb-2">🏛️ 历史命例</p>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-text">{mingli.name}</p>
                <p className="text-xs text-text-secondary mt-0.5">{mingli.bazi}</p>
              </div>
              {mingli.pattern && (
                <span className="text-[10px] px-2 py-0.5 bg-bg-subtle rounded-full text-text-secondary">
                  {mingli.pattern}
                </span>
              )}
            </div>
            <p className="text-[10px] text-text-tertiary mt-2">
              {mingli.source_type || ""} · 可信度：{mingli.credibility || "中"}
            </p>
          </div>
        )}

        {/* loading */}
        {loading && (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-gold/30 border-t-gold rounded-full animate-spin" />
          </div>
        )}

        {/* 免责声明 */}
        <p className="text-center text-[10px] text-text-tertiary py-4 pb-6">
          本软件为易经学术工具，内容仅供传统文化研究与民俗参考，
          <br />
          无任何现实指导意义，不构成人生决策依据。
        </p>
      </div>

      <BottomNav />
    </div>
  );
}