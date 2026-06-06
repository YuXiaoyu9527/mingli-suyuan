"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import ShareCard from "@/components/ShareCard";
import FeatureGate from "@/components/FeatureGate";
import { Loader2 } from "lucide-react";

function PaipanContentInner() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState({
    year: 1990, month: 5, day: 20, hour: 12, minute: 0, gender: "男", city: "",
  });
  const [hintName, setHintName] = useState("");

  // 从URL参数预填表单（历史命例跳转）
  useEffect(() => {
    const y = searchParams.get("year");
    const m = searchParams.get("month");
    const d = searchParams.get("day");
    const n = searchParams.get("name");
    if (y && m && d) {
      setForm((prev) => ({ ...prev, year: +y, month: +m, day: +d }));
    }
    if (n) setHintName(n);
  }, [searchParams]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [showTab, setShowTab] = useState<"overview"|"detail"|"ai">("overview");

  const handleSubmit = async () => {
    setLoading(true); setError(""); setShowTab("overview");
    try {
      const resp = await fetch(`${getApiUrl()}/api/full-analysis`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      setResult(await resp.json());
    } catch (e: any) {
      setError(e.message || "请求失败，请确认后端已启动");
    }
    setLoading(false);
  };

  const update = (k: string, v: any) => setForm({ ...form, [k]: v });
  const p = result?.paipan?.pillars;
  const g = result?.geju;
  const y = result?.yongshen;

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">
          八字排盘
        </h1>
        <p className="text-text-secondary text-sm mt-1">lunar-python引擎 · 真太阳时 · 格局+用神</p>
        {hintName && (
          <p className="text-xs text-gold mt-1">
            📋 已从命例导入「{hintName}」的出生日期
          </p>
        )}
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* 输入区 — 精致网格 */}
        <div className="dao-card space-y-3">
          {/* 年月日时 */}
          <div className="grid grid-cols-4 gap-2">
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-text-tertiary text-center">年</label>
              <input
                type="number" value={form.year}
                onChange={e => update("year", +e.target.value)}
                className="w-full bg-bg-subtle border border-border rounded-lg px-2 py-3
                           text-text text-base text-center focus:outline-none focus:border-gold
                           placeholder:text-text-tertiary/60"
                placeholder="1990"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-text-tertiary text-center">月</label>
              <input
                type="number" value={form.month}
                onChange={e => update("month", +e.target.value)}
                min={1} max={12}
                className="w-full bg-bg-subtle border border-border rounded-lg px-2 py-3
                           text-text text-base text-center focus:outline-none focus:border-gold
                           placeholder:text-text-tertiary/60"
                placeholder="5"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-text-tertiary text-center">日</label>
              <input
                type="number" value={form.day}
                onChange={e => update("day", +e.target.value)}
                min={1} max={31}
                className="w-full bg-bg-subtle border border-border rounded-lg px-2 py-3
                           text-text text-base text-center focus:outline-none focus:border-gold
                           placeholder:text-text-tertiary/60"
                placeholder="20"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-text-tertiary text-center">时</label>
              <input
                type="number" value={form.hour}
                onChange={e => update("hour", +e.target.value)}
                min={0} max={23}
                className="w-full bg-bg-subtle border border-border rounded-lg px-2 py-3
                           text-text text-base text-center focus:outline-none focus:border-gold
                           placeholder:text-text-tertiary/60"
                placeholder="12"
              />
            </div>
          </div>

          {/* 性别 + 城市 + 按钮 */}
          <div className="flex gap-2 items-center">
            <label className="text-[10px] text-text-tertiary flex-shrink-0">性别</label>
            <select
              value={form.gender}
              onChange={e => update("gender", e.target.value)}
              className="w-14 bg-bg-subtle border border-border rounded-lg px-2 py-3
                         text-text text-sm text-center focus:outline-none focus:border-gold"
            >
              <option>男</option>
              <option>女</option>
            </select>
            <input
              type="text" value={form.city}
              onChange={e => update("city", e.target.value)}
              placeholder="出生城市（真太阳时）"
              className="flex-1 bg-bg-subtle border border-border rounded-lg px-3 py-3
                         text-text text-xs focus:outline-none focus:border-gold placeholder:text-text-tertiary/60"
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-accent text-white px-5 py-3 rounded-lg text-sm font-medium
                         tap-active flex items-center gap-1.5 flex-shrink-0"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : "排盘"}
            </button>
          </div>
          {error && <p className="text-xs text-accent text-center">{error}</p>}
        </div>

        {/* 结果 */}
        {result && p && (
          <div className="space-y-4 anim-enter">
            {/* 日期 + 八字总览 */}
            <div className="text-center py-6 dao-card">
              <p className="text-[11px] text-text-secondary tracking-wider">
                {result.paipan.solar_date?.split(" ")[0]}
              </p>
              <p className="text-base text-text font-[family-name:var(--font-display)] mt-0.5">
                农历{result.paipan.lunar_date}
              </p>
              {result.true_solar && (
                <p className="text-[10px] text-gold mt-0.5">
                  真太阳时：{result.true_solar.corrected} ({result.true_solar.offset}分)
                </p>
              )}

              {/* 四柱 */}
              <div className="grid grid-cols-4 gap-3 mt-5">
                {["year","month","day","hour"].map((pos,i)=>{
                  const labels=["年柱","月柱","日柱","时柱"];
                  const gz=p[pos].ganzhi;
                  const isDay=pos==="day";
                  return (
                    <div key={pos} className={`${isDay?"ring-2 ring-dao-red/20":""} bg-bg-subtle/50 rounded-lg py-4`}>
                      <p className="text-[10px] text-text-secondary mb-1">{labels[i]}</p>
                      <p className="text-xl font-[family-name:var(--font-display)] text-text leading-tight">{gz[0]}</p>
                      <p className="text-xl font-[family-name:var(--font-display)] text-accent leading-tight">{gz[1]}</p>
                      <p className="text-[9px] text-text-tertiary mt-1">{p[pos].nayin}</p>
                    </div>
                  );
                })}
              </div>

              {/* 摘要行 */}
              <div className="flex items-center justify-center gap-3 mt-4 text-sm flex-wrap">
                <span className="text-text-secondary">日主</span>
                <span className="text-accent font-bold text-lg font-[family-name:var(--font-display)]">{result.paipan.rizhu}</span>
                <span className="text-text-tertiary">({result.paipan.rizhu_wuxing})</span>
                <span className="text-[10px] text-gold px-2 py-0.5 bg-gold/10 rounded-full">
                  {g?.pattern || ""}
                </span>
                <span className="text-[10px] text-text-secondary px-2 py-0.5 bg-dao-indigo/10 rounded-full">
                  {y?.wangshuai || ""}
                </span>
              </div>

              {/* 用神 */}
              {y && (
                <div className="flex items-center justify-center gap-2 mt-3 text-xs">
                  <span className="text-text-secondary">用神：</span>
                  {(y.recommended||[]).map((wx:string)=>(
                    <span key={wx} className="text-green font-medium">{wx}</span>
                  ))}
                  <span className="text-text-tertiary ml-1">忌：</span>
                  {(y.jishen||[]).map((wx:string)=>(
                    <span key={wx} className="text-accent/70">{wx}</span>
                  ))}
                </div>
              )}
            </div>

            {/* Tab切换: 概览/详情/AI解读 */}
            <div className="flex gap-1 bg-bg-subtle rounded-lg p-1">
              {[
                {id:"overview" as const,label:"概览"},
                {id:"detail" as const,label:"详情"},
                {id:"ai" as const,label:"AI解读"},
              ].map(t=>(
                <button key={t.id} onClick={()=>setShowTab(t.id)}
                  className={`flex-1 py-1.5 rounded-md text-xs transition-colors
                    ${showTab===t.id?"bg-bg text-text font-bold":"text-text-secondary"}`}>
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tab: 概览 */}
            {showTab==="overview" && (
              <div className="space-y-4 anim-enter">
                {/* 格局分析 */}
                {g && (
                  <div className="dao-card">
                    <h3 className="text-xs font-bold text-text mb-2">格局</h3>
                    <p className="text-sm text-text leading-relaxed">{g.analysis}</p>
                    {g.conditions?.length>0 && <p className="text-[11px] text-green mt-1">✅ {g.conditions.join("；")}</p>}
                    {g.reasons?.length>0 && <p className="text-[11px] text-accent mt-1">⚠ {g.reasons.join("；")}</p>}
                  </div>
                )}
                {/* 用神分析 */}
                {y && (
                  <div className="dao-card">
                    <h3 className="text-xs font-bold text-text mb-2">用神</h3>
                    <p className="text-sm text-text leading-relaxed">{y.analysis}</p>
                  </div>
                )}
                {/* 五行条 */}
                <div className="dao-card">
                  <h3 className="text-xs font-bold text-text mb-3">五行分布</h3>
                  {Object.entries(result.paipan.wuxing_scores as Record<string,number>).map(([wx,score])=>{
                    const colors:Record<string,string>={金:"bg-yellow-500",木:"bg-green-600",水:"bg-blue-500",火:"bg-red-500",土:"bg-amber-600"};
                    const total=Math.max(1,Object.values(result.paipan.wuxing_scores as number[]).reduce((a,b)=>a+b,0));
                    const pct=Math.round((score/total)*100);
                    return (
                      <div key={wx} className="flex items-center gap-2 mb-1.5">
                        <span className="text-[11px] text-text-secondary w-4">{wx}</span>
                        <div className="flex-1 h-3 bg-bg-subtle rounded-full overflow-hidden">
                          <div className={`h-full ${colors[wx]||"bg-gray-400"} rounded-full transition-all`}
                            style={{width:`${pct}%`}}/>
                        </div>
                        <span className="text-[11px] text-text-tertiary w-8 text-right">{score}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Tab: 详情 */}
            {showTab==="detail" && (
              <div className="space-y-3 anim-enter text-xs">
                {["year","month","day","hour"].map((pos,i)=>{
                  const label=["年柱","月柱","日柱","时柱"][i];
                  const d=p[pos];
                  return (
                    <div key={pos} className="dao-card py-3 px-4">
                      <p className="font-bold text-text mb-1">{label} · {d.ganzhi} · {d.nayin}</p>
                      <p className="text-text-tertiary">天干{d.gan}({d.gan_wuxing}) 地支{d.zhi}({d.zhi_wuxing})</p>
                      <p className="text-text-tertiary">十神: {pos==="day"?"日主":d.shishen} · 长生: {d.changsheng}</p>
                      <p className="text-text-tertiary">藏干: {d.canggan?.map((c:any)=>`${c.gan}(${c.score})`).join(" ")}</p>
                    </div>
                  );
                })}
                {result.paipan.zhi_relations && (
                  <div className="dao-card py-3 px-4">
                    <p className="font-bold text-text mb-1">地支关系</p>
                    {Object.entries(result.paipan.zhi_relations as Record<string,string[]>).map(([rel,items])=>{
                      if(!(items as string[]).length) return null;
                      return <p key={rel} className="text-text-tertiary">{rel}: {(items as string[]).join("、")}</p>;
                    })}
                  </div>
                )}
              </div>
            )}

            {/* Tab: AI解读 */}
            {showTab==="ai" && (
              <div className="space-y-4 anim-enter">
                {result.interpretation ? (
                  <>
                    <FeatureGate feature="AI简批（含古籍原文引用）">
                      <div className="classical-quote">
                        <p className="text-xs text-text-secondary mb-1">AI简批</p>
                        <p className="text-sm text-text leading-relaxed whitespace-pre-line">
                          {result.interpretation}
                        </p>
                      </div>
                    </FeatureGate>
                    {g?.pattern && (
                      <Link
                        href={`/xuetang?from=paipan&ref=${encodeURIComponent(g.pattern)}`}
                        className="block text-center text-xs text-gold tap-active hover:underline py-2"
                      >
                        📚 想深入了解「{g.pattern}」？→ 学堂
                      </Link>
                    )}
                  </>
                ) : (
                  <div className="dao-card text-center py-8">
                    <p className="text-text-secondary text-sm">AI解读需要配置 DeepSeek API Key</p>
                    <p className="text-[11px] text-text-tertiary mt-1">在项目根目录创建 .env 文件</p>
                  </div>
                )}
              </div>
            )}

            {/* 分享卡片 */}
            <ShareCard
              ganzhi={[p.year.ganzhi, p.month.ganzhi, p.day.ganzhi, p.hour.ganzhi]}
              rizhu={result.paipan.rizhu}
              rizhuWuxing={result.paipan.rizhu_wuxing}
              nayin={p.day.nayin}
              lunarDate={result.paipan.lunar_date}
            />

            <p className="text-center text-[10px] text-text-tertiary pb-2">
              本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义
            </p>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}

export default function PaipanPage() {
  return (
    <Suspense fallback={
      <div className="flex justify-center py-20">
        <Loader2 size={24} className="animate-spin text-gold" />
      </div>
    }>
      <PaipanContentInner />
    </Suspense>
  );
}
