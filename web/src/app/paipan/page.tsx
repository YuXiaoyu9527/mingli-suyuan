"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import LoadingSplash from "@/components/LoadingSplash";
import ShareCard from "@/components/ShareCard";
import FeatureGate from "@/components/FeatureGate";
import { jianpi, JianpiParams } from "@/lib/api";
import { Compass, Loader2 } from "lucide-react";

export default function PaipanPage() {
  const [form, setForm] = useState<JianpiParams>({
    year: 1990, month: 5, day: 20, hour: 12, minute: 0, gender: "男",
    use_ai: false,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await jianpi(form);
      setResult(data);
    } catch (e: any) {
      setError(e.message || "请求失败，请确认后端已启动");
    }
    setLoading(false);
  };

  const p = result?.paipan?.pillars;

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          八字排盘
        </h1>
        <p className="text-aged text-sm mt-1">
          公历日期 · lunar-python引擎 · 以立春换年
        </p>
      </header>

      <div className="px-5 flex-1 space-y-5">
        {/* 输入表单 */}
        <div className="dao-card space-y-4">
          <div className="flex gap-2">
            <input type="number" value={form.year} onChange={e => setForm({...form, year: +e.target.value})}
              className="flex-1 bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm focus:outline-none focus:border-vermillion" placeholder="1990"/>
            <span className="text-aged self-center">年</span>
            <input type="number" value={form.month} onChange={e => setForm({...form, month: +e.target.value})}
              min={1} max={12} className="w-16 bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm focus:outline-none focus:border-vermillion" />
            <span className="text-aged self-center">月</span>
            <input type="number" value={form.day} onChange={e => setForm({...form, day: +e.target.value})}
              min={1} max={31} className="w-16 bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm focus:outline-none focus:border-vermillion" />
            <span className="text-aged self-center">日</span>
          </div>

          <div className="flex gap-2">
            <input type="number" value={form.hour} onChange={e => setForm({...form, hour: +e.target.value})}
              min={0} max={23} className="w-16 bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm focus:outline-none focus:border-vermillion" />
            <span className="text-aged self-center">时</span>
            <input type="number" value={form.minute} onChange={e => setForm({...form, minute: +e.target.value})}
              min={0} max={59} className="w-16 bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm focus:outline-none focus:border-vermillion" />
            <span className="text-aged self-center">分</span>
            <select value={form.gender} onChange={e => setForm({...form, gender: e.target.value})}
              className="ml-auto bg-parchment-dark border border-parchment-darker rounded-lg px-3 py-2.5 text-ink text-sm">
              <option>男</option><option>女</option>
            </select>
          </div>

          <button onClick={handleSubmit} disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Compass size={18} />}
            {loading ? "排盘中..." : "开始排盘"}
          </button>
          {error && <p className="text-xs text-inauspicious text-center">{error}</p>}
        </div>

        {/* 结果展示 */}
        {result && p && (
          <div className="dao-card animate-fade-in-up space-y-4">
            {/* 日期双行展示 */}
            <div className="text-center mb-4">
              <p className="text-xs text-dao-aged tracking-wider">
                {result.paipan.solar_date?.split(" ")[0] || ""}
              </p>
              <p className="text-base text-dao-ink font-[family-name:var(--font-display)] tracking-[0.1em] mt-0.5">
                农历{result.paipan.lunar_date}
              </p>
              <p className="text-[11px] text-dao-aged-light mt-0.5">
                生肖 · {result.paipan.shengxiao || "—"}  ·  {result.paipan.rizhu}日主({result.paipan.rizhu_wuxing})
              </p>
            </div>

            {/* 四柱八字 道藏柱式 */}
            <div className="grid grid-cols-4 gap-2 text-center">
              {["year", "month", "day", "hour"].map((pos, i) => {
                const labels = ["年柱", "月柱", "日柱", "时柱"];
                const gz = p[pos].ganzhi;
                const isDay = pos === "day";
                return (
                  <div key={pos} className={`pillar-block ${isDay ? "ring-1 ring-dao-red/20" : ""}`}>
                    <p className="pillar-label">{labels[i]}</p>
                    <p className="pillar-gan">{gz[0]}</p>
                    <p className="pillar-zhi">{gz[1]}</p>
                    <p className="text-[9px] text-dao-aged-light mt-1 leading-tight">
                      {p[pos].nayin}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* 日主 + 五行 */}
            <div className="flex items-center gap-4 flex-wrap text-sm">
              <span className="text-aged">日主：</span>
              <span className="text-vermillion font-bold text-lg">{result.paipan.rizhu}</span>
              <span className="text-aged-light">({result.paipan.rizhu_wuxing})</span>
              <span className="ml-auto text-xs text-aged">
                农历：{result.paipan.lunar_date}
              </span>
            </div>

            {/* 五行分数 */}
            <div>
              <p className="text-xs text-aged mb-2">五行分布</p>
              <div className="flex gap-1 h-4 rounded-full overflow-hidden">
                {Object.entries(result.paipan.wuxing_scores as Record<string,number>).map(([wx, score]) => {
                  const colors: Record<string,string> = {金:"bg-yellow-500",木:"bg-green-600",水:"bg-blue-500",火:"bg-red-500",土:"bg-amber-600"};
                  const total = Object.values(result.paipan.wuxing_scores as Record<string,number>).reduce((a:number,b:number)=>a+b,0);
                  return <div key={wx} className={`${colors[wx]||"bg-gray-400"}`}
                    style={{width:`${(score/total)*100}%`}} title={`${wx}:${score}`} />;
                })}
              </div>
            </div>

            {/* 十神 */}
            <div className="flex flex-wrap gap-1.5 text-xs">
              {Object.entries(result.paipan.shishen_count as Record<string,number>).map(([ss,c]) =>
                <span key={ss} className="px-2 py-0.5 bg-gold/10 text-ink-light rounded-full border border-gold/20">
                  {ss}:{c}
                </span>
              )}
            </div>

            {/* 地支关系 */}
            {result.paipan.zhi_relations && Object.values(result.paipan.zhi_relations).some((v:any) => (v as any[]).length > 0) && (
              <div className="text-xs text-aged">
                {Object.entries(result.paipan.zhi_relations as Record<string,string[]>).map(([rel, items]) =>
                  items.length > 0 ? <span key={rel} className="mr-3">{rel}：{items.join("、")}</span> : null
                )}
              </div>
            )}

            {/* AI解读（付费功能） */}
            {result.interpretation && (
              <FeatureGate feature="AI简批（含古籍原文引用）">
                <div className="classical-quote mt-4">
                  <p className="text-xs text-aged mb-1">AI简批（仅供参考）</p>
                  <p className="text-sm text-ink-light leading-relaxed whitespace-pre-line">{result.interpretation}</p>
                </div>
              </FeatureGate>
            )}

            {/* 分享卡片（测测式） */}
            <ShareCard
              ganzhi={[p.year.ganzhi, p.month.ganzhi, p.day.ganzhi, p.hour.ganzhi]}
              rizhu={result.paipan.rizhu}
              rizhuWuxing={result.paipan.rizhu_wuxing}
              nayin={p.day.nayin}
              lunarDate={result.paipan.lunar_date}
            />

            {/* 古籍引用 */}
            {result.ancient_refs && (
              <details className="text-xs text-aged-light mt-2">
                <summary className="cursor-pointer">查看古籍原文引用</summary>
                <pre className="mt-2 whitespace-pre-wrap text-[11px]">{result.ancient_refs}</pre>
              </details>
            )}

            <p className="text-center text-[11px] text-aged-light">
              仅供传统文化研究与民俗参考，不构成人生决策依据
            </p>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
