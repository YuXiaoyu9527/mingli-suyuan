"use client";

import { useState, useEffect, useMemo } from "react";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";

/* ===== 节气检测 ===== */
const SOLAR_TERMS: { name: string; month: number; day: number; element: string; color: string; emoji: string }[] = [
  { name:"立春",month:2,day:4,element:"木",color:"#7A9A7E",emoji:"🌱"},
  { name:"雨水",month:2,day:19,element:"木",color:"#7A9A7E",emoji:"💧"},
  { name:"惊蛰",month:3,day:6,element:"木",color:"#7A9A7E",emoji:"⚡"},
  { name:"春分",month:3,day:21,element:"木",color:"#7A9A7E",emoji:"🌸"},
  { name:"清明",month:4,day:5,element:"木",color:"#93A87A",emoji:"🍃"},
  { name:"谷雨",month:4,day:20,element:"木",color:"#93A87A",emoji:"🌾"},
  { name:"立夏",month:5,day:6,element:"火",color:"#B5544A",emoji:"☀️"},
  { name:"小满",month:5,day:21,element:"火",color:"#B5544A",emoji:"🌿"},
  { name:"芒种",month:6,day:6,element:"火",color:"#C43A31",emoji:"🌾"},
  { name:"夏至",month:6,day:21,element:"火",color:"#C43A31",emoji:"🔥"},
  { name:"小暑",month:7,day:7,element:"火",color:"#C06050",emoji:"🌡️"},
  { name:"大暑",month:7,day:23,element:"火",color:"#C06050",emoji:"☀️"},
  { name:"立秋",month:8,day:7,element:"金",color:"#B8A88A",emoji:"🍂"},
  { name:"处暑",month:8,day:23,element:"金",color:"#B8A88A",emoji:"🍃"},
  { name:"白露",month:9,day:8,element:"金",color:"#C4B89A",emoji:"💎"},
  { name:"秋分",month:9,day:23,element:"金",color:"#C4B89A",emoji:"🌕"},
  { name:"寒露",month:10,day:8,element:"金",color:"#B8A88A",emoji:"❄️"},
  { name:"霜降",month:10,day:23,element:"金",color:"#B8A88A",emoji:"🍁"},
  { name:"立冬",month:11,day:7,element:"水",color:"#5B7B8A",emoji:"🌬️"},
  { name:"小雪",month:11,day:22,element:"水",color:"#5B7B8A",emoji:"❄️"},
  { name:"大雪",month:12,day:7,element:"水",color:"#4A6B7A",emoji:"⛄"},
  { name:"冬至",month:12,day:22,element:"水",color:"#4A6B7A",emoji:"🌑"},
  { name:"小寒",month:1,day:5,element:"水",color:"#5B7B8A",emoji:"🥶"},
  { name:"大寒",month:1,day:20,element:"水",color:"#5B7B8A",emoji:"🧊"},
];

function getCurrentSolarTerm(): typeof SOLAR_TERMS[number] {
  const now = new Date();
  const m = now.getMonth() + 1;
  const d = now.getDate();
  // 转换为年内天数，1月节气跨年：补 365 天
  const todayDOY = m * 100 + d; // 简单比较：月*100+日
  // 对 1 月节气做跨年处理
  for (let i = SOLAR_TERMS.length - 1; i >= 0; i--) {
    const t = SOLAR_TERMS[i];
    const termDOY = t.month * 100 + t.day;
    const adjusted = t.month <= 2 ? termDOY + 1200 : termDOY; // 1-2月节气视为下一年的，补1200
    const todayAdjusted = m <= 2 ? todayDOY + 1200 : todayDOY;
    if (todayAdjusted >= adjusted) return t;
  }
  return SOLAR_TERMS[SOLAR_TERMS.length - 1];
}

export default function JinriPage() {
  const router = useRouter();
  const [yiji, setYiji] = useState<any>(null);
  const [ancient, setAncient] = useState<any>(null);
  const [mingli, setMingli] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showFullText, setShowFullText] = useState(false);

  const solarTerm = useMemo(() => getCurrentSolarTerm(), []);

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
      // 真正随机选取，每次刷新不同
      setMingli(cases[Math.floor(Math.random() * cases.length)] || null);
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

  // 四宫格暗合四象 — 青龙东·朱雀南·白虎西·玄武北
  const quickLinks = [
    { icon: "🔮", label: "周易占卜", href: "/zhouyi",  desc: "六爻·梅花易数",
      siXiang: "朱雀", direction: "南", element: "火", elColor: "#C43A31" },
    { icon: "💑", label: "合婚配对", href: "/hehun",   desc: "八字缘分分析",
      siXiang: "青龙", direction: "东", element: "木", elColor: "#7A9A7E" },
    { icon: "✏️", label: "八字起名", href: "/mingli?sub=qiming", desc: "用神推荐佳名",
      siXiang: "白虎", direction: "西", element: "金", elColor: "#B8A88A" },
    { icon: "🏠", label: "阳宅风水", href: "/fengshui", desc: "八宅·九宫飞星",
      siXiang: "玄武", direction: "北", element: "水", elColor: "#5B7B8A" },
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* Calendar Hero — 日柱随节气变色 */}
      <header className="px-5 pt-8 pb-2 text-center anim-page-enter">
        {yiji && (
          <>
            {/* 节气指示 — 当前节气的五行归属 */}
            <p className="text-xs text-text-secondary tracking-[0.2em]">
              {solarTerm.emoji} {solarTerm.name} · 五行属{solarTerm.element}
              {yiji.lunar_date && <> · {yiji.lunar_date.replace(/年|月/g, (m: string) => (m === "年" ? "年" : "月")).replace(/日.*/, "日")}</>}
            </p>
            <h1
              className="text-[52px] font-[family-name:var(--font-display)] leading-none mt-2"
              style={{
                color: solarTerm.color,
                animation: "countUp 0.6s 0.2s cubic-bezier(0.22,1,0.36,1) both",
              }}
            >
              {yiji.day_ganzhi?.[0] || "——"}
            </h1>
            <p
              className="text-sm text-text-secondary tracking-wider mt-1"
              style={{ animation: "countUp 0.6s 0.4s cubic-bezier(0.22,1,0.36,1) both" }}
            >
              {yiji.week || ""} · {yiji.day_ganzhi || ""}日
              {yiji.shengxiao ? ` · 肖${yiji.shengxiao}` : ""}
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

        {/* 四宫格 — 四象方位暗合（青龙东·朱雀南·白虎西·玄武北） */}
        <div className="grid grid-cols-2 gap-3">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="dao-card flex flex-col items-center gap-2 py-5 tap-active
                         hover:shadow-md transition-all relative overflow-hidden group"
            >
              {/* 方位色条 — 卡片顶部微妙的五行色带 */}
              <div
                className="absolute top-0 left-0 right-0 h-0.5 opacity-40"
                style={{ backgroundColor: link.elColor }}
              />
              <span className="text-2xl">{link.icon}</span>
              <div className="text-center">
                <p className="text-sm font-bold text-text">{link.label}</p>
                <p className="text-[10px] text-text-tertiary mt-0.5">{link.desc}</p>
              </div>
              {/* 四象 + 方位 + 五行 标注 */}
              <div className="flex items-center gap-1.5 mt-1">
                <span className="text-[9px] text-text-tertiary/70">
                  {link.siXiang} · {link.direction} · {link.element}
                </span>
              </div>
            </Link>
          ))}
        </div>

        {/* 今日引导 — 基于日柱天干五行动态生成 */}
        {yiji?.day_gan && (() => {
          // 天干地支→五行映射
          const ganWx: Record<string, string> = { "甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水" };
          const dayWx = ganWx[yiji.day_gan] || solarTerm.element;
          const wxGuide: Record<string, { yi: string[]; ji: string; color: string }> = {
            "木": { yi: ["学习新知识","制定长期计划","早起锻炼身体","亲近大自然"], ji: "忌犹豫不决、拖延", color: "#7A9A7E" },
            "火": { yi: ["主动社交沟通","展示你的想法","推进重要项目","表达热情"], ji: "忌急躁冲动、言语伤人", color: "#B5544A" },
            "土": { yi: ["脚踏实地做事","整理收纳空间","帮助身边的人","稳扎稳打"], ji: "忌胡思乱想、过度担忧", color: "#C4A882" },
            "金": { yi: ["做决断和取舍","清理不需要的东西","制定规则边界","专注一件事"], ji: "忌优柔寡断、贪多嚼不烂", color: "#B8A88A" },
            "水": { yi: ["静心冥想思考","倾听内心直觉","深度学习研究","保存精力"], ji: "忌过度消耗、四处奔波", color: "#5B7B8A" },
          };
          const guide = wxGuide[dayWx] || wxGuide["木"];
          return (
            <div className="dao-card flex items-center gap-3 py-3 px-4">
              <span className="text-2xl">🧭</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-text">
                  今日{yiji.day_ganzhi}日 · 日主属{dayWx}
                  <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded-full" style={{color: guide.color, background: guide.color + "18"}}>{dayWx}气当令</span>
                </p>
                <p className="text-[11px] text-text-secondary mt-1 leading-relaxed">
                  宜：{guide.yi.slice(0, 3).join(" · ")}
                </p>
                <p className="text-[10px] text-text-tertiary mt-0.5">{guide.ji}</p>
              </div>
            </div>
          );
        })()}

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