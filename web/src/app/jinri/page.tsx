"use client";

import { useState, useEffect } from "react";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";

export default function JinriPage() {
  const router = useRouter();
  const [yiji, setYiji] = useState<any>(null);
  const [ancient, setAncient] = useState<any>(null);
  const [mingli, setMingli] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showFullText, setShowFullText] = useState(false);

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
      // 按日期固定选取（同日显示同一人，每日轮换）
      const idx = new Date().getDate() % Math.max(cases.length, 1);
      setMingli(cases[idx] || null);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  /** 从历史命例跳转排盘 — 自动提取八字中的时柱推算小时 */
  const handleMingliClick = (m: any) => {
    if (!m?.birth_date) return;
    const [year, month, day] = m.birth_date.split("-").map(Number);
    // 尝试从八字字符串提取时柱地支，推算出生小时
    let hour = 12; // 默认午时
    if (m.bazi) {
      const parts = m.bazi.split(/[\s　]+/).filter(Boolean);
      if (parts.length >= 4) {
        const timePillar = parts[3]; // 时柱（如"庚寅"）
        const zhi = timePillar[1];    // 地支（第二个字符）
        const zhiHour: Record<string, number> = {
          "子":0,"丑":2,"寅":4,"卯":6,"辰":8,"巳":10,
          "午":12,"未":14,"申":16,"酉":18,"戌":20,"亥":22,
        };
        hour = zhiHour[zhi] ?? 12;
      }
    }
    router.push(
      `/paipan?year=${year}&month=${month}&day=${day}&hour=${hour}&name=${encodeURIComponent(m.name)}`
    );
  };

  const quickLinks = [
    { icon: "📖", label: "古籍检索", href: "/dianji", desc: "三命通會·滴天髓" },
    { icon: "💑", label: "合婚配对", href: "/hehun",   desc: "八字缘分分析" },
    { icon: "✏️", label: "八字起名", href: "/mingli?sub=qiming", desc: "用神推荐佳名" },
    { icon: "🔮", label: "周易占卜", href: "/zhouyi",  desc: "六爻·梅花易数" },
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
        <div className="grid grid-cols-2 gap-3">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="dao-card flex flex-col items-center gap-2 py-5 tap-active hover:border-gold/40 transition-colors"
            >
              <span className="text-2xl">{link.icon}</span>
              <div className="text-center">
                <p className="text-sm font-bold text-text">{link.label}</p>
                <p className="text-[10px] text-text-tertiary mt-0.5">{link.desc}</p>
              </div>
            </Link>
          ))}
        </div>

        {/* 每日古籍 */}
        {ancient && (
          <div className="dao-card-warm relative">
            <p className="text-[10px] text-gold tracking-[0.1em] mb-2">📖 每日古籍</p>
            <div
              className="text-sm text-text leading-loose tracking-wide cursor-pointer"
              onClick={() => setShowFullText(true)}
            >
              <p className="line-clamp-3">{ancient.content}</p>
            </div>
            <p className="text-[11px] text-text-tertiary mt-2">
              ——《{ancient.source_name}》{ancient.volume}
            </p>
            {/* 研读按钮 */}
            <button
              onClick={() => setShowFullText(true)}
              className="absolute bottom-3 right-3 text-[10px] text-gold/70 hover:text-gold
                         border border-gold/30 rounded-full px-3 py-1 tap-active transition-colors"
            >
              研读全文 →
            </button>
          </div>
        )}

        {/* 历史命例 — 可点击跳转排盘 */}
        {mingli && (
          <button
            onClick={() => handleMingliClick(mingli)}
            className="w-full text-left dao-card tap-active hover:border-accent/30 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <p className="text-[10px] text-accent tracking-[0.1em] mb-2">🏛️ 历史命例</p>
              <span className="text-[10px] text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity">
                点击排盘 →
              </span>
            </div>
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
              {mingli.reliability || ""}{mingli.source ? ` · ${mingli.source}` : ""}
            </p>
          </button>
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

      {/* 古籍全文弹窗 */}
      {showFullText && ancient && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center
                     bg-black/40 backdrop-blur-sm"
          onClick={() => setShowFullText(false)}
        >
          <div
            className="bg-white w-full max-w-[430px] max-h-[70vh] overflow-y-auto
                       rounded-t-2xl sm:rounded-2xl p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs text-gold tracking-[0.1em]">
                📖 《{ancient.source_name}》{ancient.volume} · {ancient.section}
              </p>
              <button
                onClick={() => setShowFullText(false)}
                className="text-text-tertiary tap-active"
              >
                <X size={18} />
              </button>
            </div>
            <p className="text-sm text-text leading-loose whitespace-pre-line">
              {ancient.content}
            </p>
            <div className="gold-divider my-4" />
            <p className="text-[10px] text-text-tertiary text-center">
              古籍仅供参考，原文可能有OCR识别偏差
            </p>
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
}