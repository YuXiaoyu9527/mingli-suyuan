"use client";

import BottomNav from "@/components/BottomNav";
import { ScrollText, Sparkles, AlertTriangle } from "lucide-react";

export default function YijiPage() {
  // 示例数据：今日宜忌
  const today = {
    date: "2026年6月1日",
    ganzhi: "丙午日",
    jianshen: "满日",
    yi: ["读书学习", "静养休息", "整理内务", "品茶会友"],
    ji: ["冲动消费", "与人争执", "开业动土", "远行出差"],
  };

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* 顶部 */}
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          今日宜忌
        </h1>
        <p className="text-aged text-sm mt-1">
          干支合于八字 · 吉凶皆有出处
        </p>
      </header>

      <div className="px-5 flex-1 space-y-5">
        {/* 干支日期卡片 */}
        <div className="text-center py-8 card-ancient">
          <p className="text-aged text-xs mb-2">{today.date}</p>
          <div className="inline-flex items-center justify-center w-24 h-24
                         rounded-full border-2 border-vermillion mb-4">
            <span className="text-3xl font-[family-name:var(--font-display)] text-vermillion">
              丙午
            </span>
          </div>
          <p className="text-aged text-sm">
            建除十二神 ·{" "}
            <span className="text-ink font-medium">{today.jianshen}</span>
          </p>
          <p className="text-[11px] text-aged-light mt-1">
            满则盈，盈则亏——宜收尾，不宜开新
          </p>
        </div>

        {/* 宜 */}
        <div className="card-ancient">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={18} className="text-auspicious" />
            <h3 className="text-sm font-bold text-ink">宜</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {today.yi.map((item) => (
              <span
                key={item}
                className="inline-block px-3 py-1.5 bg-auspicious/10 text-auspicious
                           text-sm rounded-full border border-auspicious/20"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* 忌 */}
        <div className="card-ancient">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-inauspicious" />
            <h3 className="text-sm font-bold text-ink">忌</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {today.ji.map((item) => (
              <span
                key={item}
                className="inline-block px-3 py-1.5 bg-inauspicious/10 text-inauspicious
                           text-sm rounded-full border border-inauspicious/20"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* 古籍出处 */}
        <div className="classical-quote">
          《协纪辨方书·卷十》：
          "丙午日，火气过旺，宜静不宜动，忌嫁娶、动土。"
        </div>

        {/* 民俗科普 */}
        <div className="card-ancient">
          <div className="flex items-center gap-2 mb-3">
            <ScrollText size={18} className="text-gold" />
            <h3 className="text-sm font-bold text-ink">民俗小知识</h3>
          </div>
          <p className="text-sm text-ink-light leading-relaxed">
            所谓"建除十二神"，源自古代历法，将每日配一神煞，循环往复，共十二位：建、除、满、平、定、执、破、危、成、收、开、闭。
            今日值"满日"，取月满则亏之意。古人认为满日不宜开始新事，更适合把已经开了头的事做好收尾。就像杯子装满了水，再加就会溢出来。
          </p>
          <p className="text-xs text-aged-light mt-2">
            参考：《协纪辨方书》· 卷三 · 建除十二神考
          </p>
        </div>

        {/* 免责声明 */}
        <p className="text-center text-[11px] text-aged-light pb-4">
          仅供传统文化研究与民俗参考，不构成人生决策依据
        </p>
      </div>

      <BottomNav />
    </div>
  );
}
