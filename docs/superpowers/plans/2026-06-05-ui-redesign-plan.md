# 命理溯源 UI 重设计 — 实现计划

> **For agentic workers:** 使用 Task 工具逐任务执行。每步 checkbox (`- [ ]`) 跟踪。

**目标:** 将前端从 5 Tab 基础中式界面升级为 3 Tab（今日/排盘/学堂）专业级宣纸书院风格

**架构:** 保持 Next.js 16 App Router，不引入新依赖，复用现有 Framer Motion + Tailwind CSS v4。改动集中在 components 和 app 目录。

**技术栈:** Next.js 16 + React 19 + Tailwind CSS v4 + Framer Motion + TypeScript

---

## 文件结构

```
web/src/
├── app/
│   ├── layout.tsx          ← 修改：引入 PageTransition
│   ├── page.tsx            ← 修改：redirect /jinri
│   ├── globals.css         ← 修改：加禅意动效
│   ├── jinri/              ← 新建：今日首页
│   │   └── page.tsx
│   ├── paipan/             ← 保留改造：排盘工具页
│   │   └── page.tsx
│   ├── xuetang/            ← 保留改造：学堂
│   │   └── page.tsx
│   ├── mingli/             ← 不删但不再导航到（保留路由兼容）
│   ├── yiji/               ← 不删但不再导航到
│   ├── fengshui/           ← 保留（从今日宫格入口跳转）
│   ├── zhouyi/             ← 保留（从今日宫格入口跳转）
│   ├── dianji/             ← 保留（从今日宫格入口跳转）
│   ├── hehun/              ← 保留（从排盘页入口）
│   └── duanan/             ← 保留
├── components/
│   ├── BottomNav.tsx       ← 重写：5 Tab → 3 Tab
│   ├── CalendarHero.tsx    ← 新建：今日日历Hero
│   ├── QuickGrid.tsx       ← 新建：四宫格快捷入口
│   ├── DailyAncientCard.tsx ← 新建：每日古籍卡片
│   ├── ProgressRing.tsx    ← 新建：环形进度组件
│   ├── PWARegister.tsx     ← 已有
│   ├── PWAInstallBanner.tsx ← 已有
│   ├── FeatureGate.tsx     ← 已改
│   ├── ShareCard.tsx       ← 保留
│   ├── DailyWisdom.tsx     ← 保留
│   └── LoadingSplash.tsx   ← 保留
└── lib/
    └── api.ts              ← 保留不改
```

---

### Task 1: 重写 BottomNav 为 3 Tab

**文件:**
- 修改: `web/src/components/BottomNav.tsx`

现有 5 Tab → 改为 3 Tab：今日(🏮) · 排盘(☯) · 学堂(📚)

- [ ] **Step 1: 重写 BottomNav.tsx**

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { id: "jinri", label: "今日", icon: "🏮", href: "/jinri" },
  { id: "paipan", label: "排盘", icon: "☯", href: "/paipan" },
  { id: "xuetang", label: "学堂", icon: "📚", href: "/xuetang" },
];

export default function BottomNav() {
  const pathname = usePathname();
  const isActive = (id: string) => pathname.startsWith(`/${id}`);

  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px]
                    bg-white/95 backdrop-blur-xl safe-bottom z-50 border-t border-border">
      <div className="flex items-center justify-around h-[56px]">
        {tabs.map((tab) => {
          const active = isActive(tab.id);
          return (
            <Link key={tab.id} href={tab.href}
              className={`flex flex-col items-center justify-center gap-0.5
                         min-w-[56px] py-1 rounded-lg tap-active transition-colors
                         ${active ? "text-accent" : "text-text-tertiary"}`}>
              <span className={`text-lg ${active ? "opacity-100" : "opacity-50"}`}>{tab.icon}</span>
              <span className={`text-[10px] ${active ? "font-semibold" : "font-normal"}`}>{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd web && npx tsc --noEmit 2>&1 | head -10
```

---

### Task 2: 增强动画系统（禅意节奏）

**文件:**
- 修改: `web/src/app/globals.css`

在现有 `anim-enter` 和 `anim-stagger` 基础上，增加更丰富的禅意动效。

- [ ] **Step 1: 在 globals.css 末尾追加动画**

```css
/* === 禅意动效系统 === */

/* 数字计数动画 */
@keyframes countUp {
  from { opacity: 0; transform: translateY(0.5em); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 慢速浮现（600ms，用于页面切换） */
@keyframes fadeInSlow {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* 从下方滑入 */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 缩放弹入 */
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}

/* 应用类 */
.anim-page-enter {
  animation: fadeInSlow 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.anim-slide-up {
  animation: slideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.anim-scale-in {
  animation: scaleIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.anim-count-up {
  animation: countUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* 卡片交错——基于 anim-stagger 扩展更多级 */
.anim-stagger-8 > *:nth-child(1) { animation: slideUp 0.45s 0.00s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(2) { animation: slideUp 0.45s 0.06s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(3) { animation: slideUp 0.45s 0.12s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(4) { animation: slideUp 0.45s 0.18s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(5) { animation: slideUp 0.45s 0.24s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(6) { animation: slideUp 0.45s 0.30s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(7) { animation: slideUp 0.45s 0.36s cubic-bezier(0.22,1,0.36,1) both; }
.anim-stagger-8 > *:nth-child(8) { animation: slideUp 0.45s 0.42s cubic-bezier(0.22,1,0.36,1) both; }
```

- [ ] **Step 2: 验证 CSS**

```bash
cd web && npx tailwindcss -i src/app/globals.css --dry-run 2>&1 | tail -1
```

---

### Task 3: 创建今日首页（CalendarHero + 内容卡片）

**文件:**
- 创建: `web/src/app/jinri/page.tsx`
- 修改: `web/src/app/page.tsx`（redirect → /jinri）

- [ ] **Step 1: 更新根路由**

```tsx
// web/src/app/page.tsx
import { redirect } from "next/navigation";
export default function Home() {
  redirect("/jinri");
}
```

- [ ] **Step 2: 创建今日首页**

```tsx
// web/src/app/jinri/page.tsx
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
      // 并行加载今日数据
      const [yResp, aResp, mResp] = await Promise.all([
        fetch(`${getApiUrl()}/api/yiji`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }),
        fetch(`${getApiUrl()}/api/search`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: "日", top_k: 1 }) }),
        fetch(`${getApiUrl()}/api/mingli`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }),
      ]);
      setYiji(await yResp.json());
      const aData = await aResp.json();
      setAncient(aData.results?.[0] || null);
      const mData = await mResp.json();
      // 随机取一个命例
      const cases = mData.cases || [];
      setMingli(cases[Math.floor(Math.random() * cases.length)] || null);
    } catch (e) { console.error(e); }
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
              甲辰年 · {yiji.lunar_date?.replace(/年|月/g, (m: string) => m === "年" ? " · " : " · ") || ""}
            </p>
            <h1 className="text-[52px] font-[family-name:var(--font-display)] text-text leading-none mt-2 anim-count-up"
              style={{ animationDelay: "0.2s" }}>
              {yiji.day_ganzhi?.[0] || "——"}
            </h1>
            <p className="text-sm text-text-secondary tracking-wider mt-1" style={{ animationDelay: "0.4s" }}>
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
            <Link key={link.href} href={link.href}
              className="dao-card flex flex-col items-center gap-1.5 py-4 tap-active hover:border-gold/40 transition-colors">
              <span className="text-2xl">{link.icon}</span>
              <span className="text-xs text-text">{link.label}</span>
            </Link>
          ))}
        </div>

        {/* 每日古籍 */}
        {ancient && (
          <Link href={`/xuetang?ref=${encodeURIComponent(ancient.section || "")}`}
            className="block dao-card-warm tap-active hover:shadow-md transition-shadow">
            <p className="text-[10px] text-gold tracking-[0.1em] mb-2">📖 每日古籍</p>
            <p className="text-sm text-text leading-relaxed line-clamp-3">
              {ancient.content}
            </p>
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
              <span className="text-[10px] px-2 py-0.5 bg-bg-subtle rounded-full text-text-secondary">
                {mingli.pattern || ""}
              </span>
            </div>
            <p className="text-[10px] text-text-tertiary mt-2">
              {mingli.source_type || ""} · 可信度：{mingli.credibility || "中"}
            </p>
          </div>
        )}

        {/* 免责声明 */}
        <p className="text-center text-[10px] text-text-tertiary py-4">
          本软件为易经学术工具，内容仅供传统文化研究与民俗参考，<br/>
          无任何现实指导意义，不构成人生决策依据。
        </p>
      </div>

      <BottomNav />
    </div>
  );
}
```

- [ ] **Step 3: 验证编译**

```bash
cd web && npx tsc --noEmit 2>&1 | grep -i error | head -10
```

---

### Task 4: 改造排盘页为独立问真式工具页

**文件:**
- 修改: `web/src/app/paipan/page.tsx`

当前 paipan/page.tsx 已经是独立的排盘页（输入在上、结果在下、Tab切换），内容较完整。主要改造：
1. 标题简化
2. 结果区默认展示"概览" Tab
3. 添加"想深入了解？→ 学堂"跳转

- [ ] **Step 1: 在排盘结果底部添加学堂跳转**

在 `paipan/page.tsx` 的 AI 解读 Tab 内容区底部（`result.interpretation` 后面），添加：

```tsx
{/* 在 AI Tab 底部，result.interpretation 渲染之后 */}
{result.interpretation && g && (
  <Link href={`/xuetang?from=paipan&ref=${encodeURIComponent(g.pattern)}`}
    className="block mt-3 text-center text-xs text-gold tap-active hover:underline">
    📚 想深入了解「{g.pattern}」？→ 学堂
  </Link>
)}
```

需要在文件顶部添加 import：
```tsx
import Link from "next/link";
```

- [ ] **Step 2: 验证编译**

---

### Task 5: 学堂页添加进度环 + 章节卡片改造

**文件:**
- 修改: `web/src/app/xuetang/page.tsx`
- 创建: `web/src/components/ProgressRing.tsx`

- [ ] **Step 1: 创建 ProgressRing 组件**

```tsx
// web/src/components/ProgressRing.tsx
"use client";

interface ProgressRingProps {
  progress: number; // 0-100
  size?: number;
  strokeWidth?: number;
}

export default function ProgressRing({ progress, size = 56, strokeWidth = 5 }: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* 背景圈 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
        />
        {/* 进度圈 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-accent)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
      </svg>
      <span className="absolute text-sm font-bold text-accent">
        {Math.round(progress)}%
      </span>
    </div>
  );
}
```

- [ ] **Step 2: 在学堂首页顶部插入进度环**

在 `xuetang/page.tsx` 的章节列表视图头部（`<header>` 之后，`{chapters.map(...)}` 之前），添加：

```tsx
{/* 学习进度卡片 — 在 header 后面、章节列表前面 */}
{!loading && chapters.length > 0 && (
  <div className="dao-card-warm mb-4 flex items-center gap-4 anim-scale-in">
    <ProgressRing progress={
      Math.round((Object.keys(passed).filter(k => passed[k]).length / Math.max(chapters.length, 1)) * 100)
    } />
    <div className="flex-1">
      <p className="text-sm font-bold text-text">学习进度</p>
      <p className="text-xs text-text-secondary mt-0.5">
        已完成 {Object.values(passed).filter(Boolean).length}/{chapters.length} 章
      </p>
      {/* 找到第一个未完成的章节 */}
      {(() => {
        const next = chapters.find(ch => !passed[ch.id] && isUnlocked(ch));
        return next ? (
          <button onClick={() => loadChapter(next.id)}
            className="text-xs text-accent mt-1 font-medium tap-active">
            继续学习 → {next.title}
          </button>
        ) : (
          <p className="text-xs text-green mt-1">🎉 全部通关！</p>
        );
      })()}
    </div>
  </div>
)}
```

- [ ] **Step 3: 添加场景跳转参数处理**

在 `xuetang/page.tsx` 的 `useEffect` 中检测 URL 参数，自动跳转到对应章节：

```tsx
// 在已有的 useEffect (loadChapters) 之后添加：
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const from = params.get("from");
  const ref = params.get("ref");
  if (from && chapters.length > 0) {
    // 从排盘或其他页面跳转过来，匹配相关章节
    const matched = chapters.find(ch =>
      ch.title.includes(ref || "") || ch.subtitle.includes(ref || "")
    );
    if (matched) {
      loadChapter(matched.id);
    }
  }
}, [chapters]);
```

- [ ] **Step 4: 验证编译**

---

### Task 6: 验证全流程

- [ ] **Step 1: 启动前端验证**

```bash
cd web && npm run dev
```

检查：
- `http://localhost:3000` → 自动跳转 `/jinri`
- `/jinri` → Calendar Hero + 宜忌 + 宫格 + 古籍卡片
- `/paipan` → 问真式排盘页
- `/xuetang` → 进度环 + 章节列表
- BottomNav 三个 Tab 正确高亮

- [ ] **Step 2: 确认旧页面仍可访问**

- `/yiji` → 老黄历页（保留但不再主导航）
- `/fengshui` → 风水页（从宫格入口跳转）
- `/zhouyi` → 周易页（从宫格入口跳转）
- `/dianji` → 典籍页（从宫格入口跳转）

---

### Task 7: 提交

```bash
git add .
git commit -m "feat: UI redesign Phase 1 — 3 Tab navigation with Calendar Hero and zen animations

- BottomNav: 5 tabs → 3 tabs (今日/排盘/学堂)
- New 今日 homepage with Calendar Hero + 宜忌 + 宫格入口
- ProgressRing component for 学堂
- Zen animation system (fadeInSlow, slideUp, scaleIn, countUp)
- Paipan page: add 学堂 deep-link from AI interpretation
- Xuetang page: progress ring + deep-link parameter handling
- Root redirect: / → /jinri"
```

---

## 实现后检查清单

- [ ] `localhost:3000` 首页 → 今日页面
- [ ] 今日页显示日历 Hero + 宜忌 + 冲煞 + 四宫格 + 古籍 + 命例
- [ ] 底部 3 Tab 导航正常
- [ ] 排盘页功能正常，输入→结果→格局用神→AI解读
- [ ] 排盘 AI 解读底部有学堂跳转链接
- [ ] 学堂页顶部有进度环
- [ ] 免责声明在所有页面底部
- [ ] 移动端 375-430px 适配正常
- [ ] 旧路由（/yiji /fengshui /zhouyi /dianji）仍可访问