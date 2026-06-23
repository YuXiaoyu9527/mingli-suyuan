"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import ShareCard from "@/components/ShareCard";
import FeatureGate from "@/components/FeatureGate";
import { Loader2, Sun, Moon, Users, ChevronDown, Heart, PenLine } from "lucide-react";

/* ===== 安全 localStorage 工具 ===== */
function safeGet<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try { return JSON.parse(localStorage.getItem(key) || "null") ?? fallback; }
  catch { return fallback; }
}

/* ===== 莫兰迪五行色（用于四柱干支着色） ===== */
const WX_HEX: Record<string, string> = {
  "金": "#B8A88A", "木": "#7A9A7E", "水": "#5B7B8A", "火": "#B5544A", "土": "#C4A882",
};

/* ===== 五行调和知识库（排盘生活应用层） ===== */
const WX_ADVICE: Record<string, { colors: string[]; items: string[]; actions: string[]; direction: string }> = {
  "金": { colors: ["白","银","浅灰","米白"], items: ["金属饰品","银质项链","白色手表","圆形镜子"], actions: ["整理桌面/断舍离","制定清晰的时间表","早上7-9点做重要决策"], direction: "西北" },
  "木": { colors: ["绿","青","翠绿","浅蓝"], items: ["绿植盆栽","木质手串","棉麻衣物","植物精油"], actions: ["早起锻炼舒展身体","养一盆绿植放在东方位","制定长期规划"], direction: "东" },
  "水": { colors: ["黑","深蓝","藏青","深灰"], items: ["黑色水杯","蓝色水晶","黑曜石手链","流水摆件"], actions: ["多喝水/泡茶","冥想静坐10分钟","重要洽谈安排在下午"], direction: "北" },
  "火": { colors: ["红","紫","玫红","橙红"], items: ["红色围巾","南红玛瑙","红绳手链","暖光灯"], actions: ["主动社交联系三人","重要电话在中午11-1点打","点燃香薰蜡烛"], direction: "南" },
  "土": { colors: ["黄","棕","卡其","米色"], items: ["黄水晶","陶瓷茶具","黄玉貔貅","棕色皮具"], actions: ["脚踏实地做好手头事","每工作45分钟休息5分钟","周末去公园踩踩泥土"], direction: "西南" },
};
const WX_AVOID: Record<string, string> = { "金":"忌红色（火克金）","木":"忌白色（金克木）","水":"忌黄色（土克水）","火":"忌黑色（水克火）","土":"忌绿色（木克土）" };

/* ===== 经典命例（空白期推荐·随机展示4个） ===== */
const FEATURED_CASES = [
  { name: "司马光", year: 1019, month: 11, day: 17, hour: 8,  desc: "北宋名臣 · 正官格",    emoji: "🏛️" },
  { name: "范蠡",   year: -536, month: 1,  day: 1,  hour: 6,  desc: "商圣 · 财旺身强",      emoji: "💰" },
  { name: "诸葛亮", year: 181,  month: 7,  day: 23, hour: 12, desc: "蜀汉丞相 · 杀印相生",    emoji: "🎯" },
  { name: "苏轼",   year: 1037, month: 1,  day: 8,  hour: 10, desc: "东坡居士 · 食神生财",    emoji: "📜" },
  { name: "李白",   year: 701,  month: 2,  day: 8,  hour: 10, desc: "诗仙 · 食伤泄秀",       emoji: "🍷" },
  { name: "康熙",   year: 1654, month: 5,  day: 4,  hour: 10, desc: "清圣祖 · 七杀有制",      emoji: "👑" },
  { name: "岳飞",   year: 1103, month: 3,  day: 24, hour: 12, desc: "武穆 · 杀刃两显",        emoji: "⚔️" },
  { name: "王阳明", year: 1472, month: 10, day: 31, hour: 6,  desc: "心学宗师 · 伤官配印",    emoji: "🧘" },
  { name: "张居正", year: 1525, month: 5,  day: 24, hour: 8,  desc: "大明首辅 · 正印制伤",    emoji: "📋" },
  { name: "武则天", year: 624,  month: 2,  day: 17, hour: 12, desc: "则天女皇 · 杀印相生",    emoji: "👸" },
];

/** 从命例数组中随机选取 n 个不重复的 */
function pickRandom<T>(arr: T[], n: number): T[] {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

interface BaziProfile {
  id: string; name: string;
  year: number; month: number; day: number; hour: number; gender: string;
}

function PaipanContentInner() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState({
    year: 1990, month: 5, day: 20, hour: 12, minute: 0, gender: "男", city: "",
  });
  const [calendarType, setCalendarType] = useState<"solar" | "lunar">("solar");
  const [hintName, setHintName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [showTab, setShowTab] = useState<"overview" | "detail" | "ai">("overview");
  const [profiles, setProfiles] = useState<BaziProfile[]>([]);
  const [showProfilePicker, setShowProfilePicker] = useState(false);
  // 每次进入页面随机选 4 个经典命例（会话内稳定）
  const [featuredCases] = useState(() => pickRandom(FEATURED_CASES, 4));

  // 读取亲友档案
  useEffect(() => {
    setProfiles(safeGet<BaziProfile[]>("bazi_profiles", []));
  }, []);

  // 从URL参数预填表单（历史命例/亲友档案跳转）
  useEffect(() => {
    const y = searchParams.get("year");
    const m = searchParams.get("month");
    const d = searchParams.get("day");
    const h = searchParams.get("hour");
    const n = searchParams.get("name");
    if (y && m && d) {
      setForm((prev) => ({
        ...prev,
        year: +y, month: +m, day: +d,
        hour: h ? +h : prev.hour,
      }));
    }
    if (n) setHintName(n);
  }, [searchParams]);

  const handleSubmit = async () => {
    setLoading(true); setError(""); setShowTab("overview");
    try {
      const resp = await fetch(`${getApiUrl()}/api/full-analysis`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, calendar_type: calendarType }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      setResult(await resp.json());
    } catch (e: any) {
      setError(e.message || "请求失败，请确认后端已启动");
    }
    setLoading(false);
  };

  /** 从经典命例或亲友档案预填表单 */
  const fillFromCase = (y: number, m: number, d: number, h?: number, n?: string) => {
    setForm({ ...form, year: y, month: m, day: d, hour: h ?? 12, minute: 0 });
    if (n) setHintName(n);
    setShowProfilePicker(false);
  };

  const update = (k: string, v: any) => setForm({ ...form, [k]: v });
  const p = result?.paipan?.pillars;
  const g = result?.geju;
  const y_ = result?.yongshen;

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-6 pt-6 pb-3">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">
          八字排盘
        </h1>
        <p className="text-text-secondary text-sm mt-1">
          lunar-python引擎 · 真太阳时校正 · 格局+用神自动判定
        </p>
        {hintName && (
          <p className="text-xs text-gold mt-1">
            📋 已导入「{hintName}」的出生日期
          </p>
        )}
      </header>

      <div className="px-6 flex-1 space-y-6">
        {/* ===== 档案导入入口 ===== */}
        {profiles.length > 0 && (
          <div className="relative">
            <button
              onClick={() => setShowProfilePicker(!showProfilePicker)}
              className="w-full flex items-center justify-between gap-2 px-4 py-2.5
                         bg-bg-subtle border border-border rounded-xl text-xs text-text-secondary
                         hover:border-gold/40 transition-colors tap-active"
            >
              <span className="flex items-center gap-2">
                <Users size={14} className="text-gold" />
                从亲友档案库导入
              </span>
              <ChevronDown
                size={14}
                className={`transition-transform ${showProfilePicker ? "rotate-180" : ""}`}
              />
            </button>
            {showProfilePicker && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-border
                             rounded-xl shadow-lg z-30 max-h-48 overflow-y-auto anim-enter">
                {profiles.map((pro) => (
                  <button
                    key={pro.id}
                    onClick={() => fillFromCase(pro.year, pro.month, pro.day, pro.hour, pro.name)}
                    className="w-full text-left px-4 py-3 hover:bg-bg-subtle transition-colors
                               flex items-center justify-between border-b border-border/50 last:border-0"
                  >
                    <span className="text-sm text-text">{pro.name}</span>
                    <span className="text-[10px] text-text-tertiary">
                      {pro.year}.{pro.month}.{pro.day} · {pro.gender}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ===== 输入区 ===== */}
        <div className="dao-card space-y-3">
          {/* 公历/农历切换 */}
          <div className="flex gap-1 bg-bg-subtle rounded-lg p-1">
            {([
              { id: "solar" as const, label: "公历", icon: Sun, desc: "阳历" },
              { id: "lunar" as const, label: "农历", icon: Moon, desc: "阴历" },
            ]).map((t) => (
              <button
                key={t.id}
                onClick={() => setCalendarType(t.id)}
                className={`flex-1 py-2 rounded-md text-sm transition-all flex items-center justify-center gap-1.5
                  ${calendarType === t.id
                    ? "bg-white text-text font-bold shadow-sm"
                    : "text-text-tertiary"}`}
              >
                <t.icon size={14} />
                {t.label}
                <span className="text-[9px] opacity-50 hidden sm:inline">{t.desc}</span>
              </button>
            ))}
          </div>

          {/* 年月日时分 5列 */}
          <div className="grid grid-cols-5 gap-2">
            {([
              { k: "year",   label: calendarType === "solar" ? "年" : "农年", ph: "1990",  min: 1900, max: 2100 },
              { k: "month",  label: "月",  ph: "5",   min: 1,    max: calendarType === "lunar" ? 12 : 12 },
              { k: "day",    label: "日",  ph: "20",  min: 1,    max: calendarType === "lunar" ? 30 : 31 },
              { k: "hour",   label: "时",  ph: "12",  min: 0,    max: 23 },
              { k: "minute", label: "分",  ph: "00",  min: 0,    max: 59 },
            ]).map(({ k, label, ph, min, max }) => (
              <div key={k} className="flex flex-col gap-1">
                <label className="text-[10px] text-text-tertiary text-center">{label}</label>
                <input
                  type="number"
                  value={(form as any)[k]}
                  onChange={(e) => update(k, +e.target.value)}
                  min={min} max={max}
                  className="w-full bg-bg-subtle border border-border rounded-lg px-1 py-3
                             text-text text-base text-center focus:outline-none focus:border-gold
                             placeholder:text-text-tertiary/60"
                  placeholder={ph}
                />
              </div>
            ))}
          </div>

          {/* 性别 + 城市 + 按钮 */}
          <div className="flex gap-2 items-center">
            <label className="text-[10px] text-text-tertiary flex-shrink-0">性别</label>
            <select
              value={form.gender}
              onChange={(e) => update("gender", e.target.value)}
              className="w-14 bg-bg-subtle border border-border rounded-lg px-2 py-3
                         text-text text-sm text-center focus:outline-none focus:border-gold"
            >
              <option>男</option>
              <option>女</option>
            </select>
            <input
              type="text" value={form.city}
              onChange={(e) => update("city", e.target.value)}
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

        {/* ===== 未排盘：推荐经典命例 ===== */}
        {!result && (
          <div className="space-y-3 anim-enter">
            <p className="text-xs text-text-tertiary text-center tracking-wider">
              — 经典命例 · 点击一键体验 —
            </p>
            <div className="grid grid-cols-2 gap-3">
              {featuredCases.map((c) => (
                <button
                  key={c.name}
                  onClick={() => fillFromCase(c.year, c.month, c.day, c.hour, c.name)}
                  className="dao-card py-4 px-4 text-left tap-active hover:border-gold/40
                             transition-all group"
                >
                  <span className="text-2xl">{c.emoji}</span>
                  <p className="text-sm font-bold text-text mt-2">{c.name}</p>
                  <p className="text-[10px] text-text-tertiary mt-0.5 leading-relaxed">{c.desc}</p>
                  <p className="text-[9px] text-gold/60 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    点击导入排盘 →
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ===== 已排盘：结果展示 ===== */}
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
                      <p className="text-xl font-[family-name:var(--font-display)] leading-tight"
                        style={{color: WX_HEX[p[pos].gan_wuxing] || "#1C1814"}}>{gz[0]}</p>
                      <p className="text-xl font-[family-name:var(--font-display)] leading-tight"
                        style={{color: WX_HEX[p[pos].zhi_wuxing] || "#1C1814"}}>{gz[1]}</p>
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
                <Link
                  href={`/dianji?q=${encodeURIComponent(g?.pattern || "")}`}
                  className="text-[10px] text-gold px-2 py-0.5 bg-gold/10 rounded-full hover:bg-gold/20 transition-colors"
                >
                  {g?.pattern || ""}
                </Link>
                <span className="text-[10px] text-text-secondary px-2 py-0.5 bg-dao-indigo/10 rounded-full">
                  {y_?.wangshuai || ""}
                </span>
              </div>

              {/* 用神 */}
              {y_ && (
                <div className="flex items-center justify-center gap-2 mt-3 text-xs">
                  <span className="text-text-secondary">用神：</span>
                  {(y_.recommended||[]).map((wx:string)=>(
                    <span key={wx} className="text-green font-medium">{wx}</span>
                  ))}
                  <span className="text-text-tertiary ml-1">忌：</span>
                  {(y_.jishen||[]).map((wx:string)=>(
                    <span key={wx} className="text-accent/70">{wx}</span>
                  ))}
                </div>
              )}
            </div>

            {/* ===== 生活应用层 — 基于主用神的五行调和 ===== */}
            {y_ && y_.recommended?.length > 0 && (() => {
              const mainWx = y_.recommended[0];
              const adv = WX_ADVICE[mainWx];
              if (!adv) return null;
              // 只展示跟主用神相克的那个忌神（避免列一堆禁忌制造焦虑）
              const shengKe: Record<string, string> = { "木":"金","火":"水","土":"木","金":"火","水":"土" };
              const mainJi = shengKe[mainWx]; // 克主用神的那个五行
              const hasJi = y_.jishen?.includes(mainJi);
              return (
                <div className="dao-card space-y-3" style={{ borderColor: "rgba(201,169,110,0.3)" }}>
                  <p className="text-xs font-bold text-text flex items-center gap-1.5">
                    🧭 五行调和 · 生活应用
                    <span className="text-[10px] text-text-tertiary font-normal">
                      主用神{mainWx}{y_.recommended.length > 1 ? `，辅${y_.recommended.slice(1).join("、")}` : ""}
                    </span>
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-bg-subtle rounded-lg p-3">
                      <p className="text-[10px] text-text-tertiary mb-1">👔 穿衣颜色</p>
                      <p className="text-xs text-text font-medium">{adv.colors.slice(0, 3).join("、")}色</p>
                    </div>
                    <div className="bg-bg-subtle rounded-lg p-3">
                      <p className="text-[10px] text-text-tertiary mb-1">🧭 有利方位</p>
                      <p className="text-xs text-text font-medium">{adv.direction}方</p>
                    </div>
                    <div className="bg-bg-subtle rounded-lg p-3">
                      <p className="text-[10px] text-text-tertiary mb-1">🎒 随身物品</p>
                      <p className="text-xs text-text font-medium">{adv.items.slice(0, 2).join(" · ")}</p>
                    </div>
                    <div className="bg-bg-subtle rounded-lg p-3">
                      <p className="text-[10px] text-text-tertiary mb-1">⚠️ 需要注意</p>
                      <p className="text-xs text-text font-medium leading-relaxed">
                        {hasJi ? `少用${mainJi}性颜色，${mainJi === "火" ? "避免急躁冲动" : mainJi === "水" ? "保持温暖干燥" : mainJi === "金" ? "多些包容弹性" : mainJi === "木" ? "专注少分散" : "保持心态稳定"}` : "保持平衡即可"}
                      </p>
                    </div>
                  </div>
                  <div className="bg-bg-subtle rounded-lg p-3">
                    <p className="text-[10px] text-text-tertiary mb-1">📋 具体行动建议</p>
                    <p className="text-xs text-text leading-relaxed">{adv.actions.join("；") + "。"}</p>
                  </div>
                </div>
              );
            })()}

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
                {g && (
                  <div className="dao-card">
                    <h3 className="text-xs font-bold text-text mb-2">格局</h3>
                    <p className="text-sm text-text leading-relaxed">{g.analysis}</p>
                    {g.conditions?.length>0 && <p className="text-[11px] text-green mt-1">✅ {g.conditions.join("；")}</p>}
                    {g.reasons?.length>0 && <p className="text-[11px] text-accent mt-1">⚠ {g.reasons.join("；")}</p>}
                  </div>
                )}
                {y_ && (
                  <div className="dao-card">
                    <h3 className="text-xs font-bold text-text mb-2">用神</h3>
                    <p className="text-sm text-text leading-relaxed">{y_.analysis}</p>
                  </div>
                )}
                <div className="dao-card">
                  <h3 className="text-xs font-bold text-text mb-3">五行分布</h3>
                  {Object.entries(result.paipan.wuxing_scores as Record<string,number>).map(([wx,score])=>{
                    // 莫兰迪五行色 — 低饱和度古典色卡
                    const wxColors:Record<string,string>={金:"var(--color-wx-gold)",木:"var(--color-wx-wood)",水:"var(--color-wx-water)",火:"var(--color-wx-fire)",土:"var(--color-wx-earth)"};
                    const wxLabels:Record<string,string>={金:"金",木:"木",水:"水",火:"火",土:"土"};
                    const total=Math.max(1,Object.values(result.paipan.wuxing_scores as number[]).reduce((a,b)=>a+b,0));
                    const pct=Math.round((score/total)*100);
                    return (
                      <div key={wx} className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-text-secondary w-4 font-[family-name:var(--font-display)]">{wxLabels[wx]||wx}</span>
                        <div className="flex-1 h-3 bg-bg-subtle rounded-full overflow-hidden">
                          <div className="h-full rounded-full transition-all duration-700"
                            style={{width:`${pct}%`, backgroundColor:wxColors[wx]||"#999"}}/>
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

            {/* ===== 功能卡片：合婚 + 起名 ===== */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              <Link
                href={`/hehun?m_year=${form.year}&m_month=${form.month}&m_day=${form.day}&m_hour=${form.hour}`}
                className="dao-card p-4 text-center tap-active hover:border-accent/30 transition-all group"
              >
                <Heart size={20} className="text-accent mx-auto mb-2 group-hover:scale-110 transition-transform" />
                <p className="text-sm font-bold text-text">合婚配对</p>
                <p className="text-[10px] text-text-tertiary mt-1">输入对方八字 · 缘分分析</p>
              </Link>
              <Link
                href={`/mingli?sub=qiming&year=${form.year}&month=${form.month}&day=${form.day}`}
                className="dao-card p-4 text-center tap-active hover:border-gold/40 transition-all group"
              >
                <PenLine size={20} className="text-gold mx-auto mb-2 group-hover:scale-110 transition-transform" />
                <p className="text-sm font-bold text-text">八字起名</p>
                <p className="text-[10px] text-text-tertiary mt-1">基于用神 · 推荐佳名</p>
              </Link>
            </div>

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
