"use client";

/**
 * 潮汐式日签组件
 * 每次加载随机显示一条古籍智慧短句
 * 灵感来源: 潮汐App 的每日禅意文案
 */

import { useEffect, useState } from "react";

// 日签库（从我们的古籍中精选）
const WISDOMS = [
  { text: "五行者，往来乎天地之间而不穷者也。", source: "《三命通会·卷一》" },
  { text: "无名天地之始，有名万物之母。", source: "《道德经》" },
  { text: "一阴一阳之谓道，继之者善也。", source: "《易经·系辞》" },
  { text: "天行健，君子以自强不息。", source: "《易经·乾卦》" },
  { text: "地势坤，君子以厚德载物。", source: "《易经·坤卦》" },
  { text: "顺则相生，逆则相克。", source: "《三命通会·卷一》" },
  { text: "知命者不怨天，自知者不怨人。", source: "《中庸》" },
  { text: "木主于东应春，火主于南应夏。", source: "《三命通会·论五行》" },
  { text: "气乘风则散，界水则止。", source: "《葬书》" },
  { text: "满则盈，盈则亏，故满日不宜开新。", source: "《协纪辨方书》" },
  { text: "善为士者不武，善战者不怒。", source: "《道德经》" },
  { text: "人法地，地法天，天法道，道法自然。", source: "《道德经》" },
];

export default function DailyWisdom() {
  const [wisdom, setWisdom] = useState(WISDOMS[0]);

  useEffect(() => {
    // 基于日期选择日签（保证同一天显示同一句）
    const today = new Date();
    const dayOfYear = Math.floor(
      (today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / 86400000
    );
    setWisdom(WISDOMS[dayOfYear % WISDOMS.length]);
  }, []);

  return (
    <div className="text-center px-8 py-6">
      <p className="text-xs text-dao-aged tracking-[0.15em] mb-3">
        今 日 一 签
      </p>
      <p className="text-base text-dao-ink-light leading-relaxed font-[family-name:var(--font-body)] italic">
        「{wisdom.text}」
      </p>
      <p className="text-[11px] text-dao-aged-light mt-3 tracking-wider">
        {wisdom.source}
      </p>
    </div>
  );
}
