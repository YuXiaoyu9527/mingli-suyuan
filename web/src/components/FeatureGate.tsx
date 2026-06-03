"use client";

/**
 * 功能分层组件
 * 灵感来源: 问真八字 Freemium 模式
 *
 * 免费功能: 排盘/今日宜忌/基础检索/断案录第一章
 * 付费功能: AI简批/深度命例/全部断案录/古籍溯源详细
 */

import { useState } from "react";
import { Crown } from "lucide-react";

type Tier = "free" | "premium";

const PREMIUM_FEATURES = [
  "AI简批（含古籍原文引用）",
  "完整断案录题库",
  "历史命例详情",
  "深度古籍溯源",
];

export default function FeatureGate({
  feature,
  children,
}: {
  feature: string;
  children: React.ReactNode;
}) {
  const [tier] = useState<Tier>("free"); // 默认免费，后续接用户系统

  if (tier === "premium" || !PREMIUM_FEATURES.includes(feature)) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {/* 模糊遮罩 */}
      <div className="blur-sm pointer-events-none opacity-40">
        {children}
      </div>

      {/* 解锁提示 */}
      <div className="absolute inset-0 flex flex-col items-center justify-center
                      bg-bg/60 backdrop-blur-[2px] rounded-lg">
        <Crown size={24} className="text-gold mb-2" />
        <p className="text-xs text-text font-medium mb-1">
          解锁{feature}
        </p>
        <p className="text-[11px] text-text-secondary mb-3">
          古籍溯源 · 命理详解 · 深度学习
        </p>
        <button className="px-4 py-1.5 bg-gold text-white text-xs rounded-full
                           font-medium tap-active">
          ¥9.9/月 开通
        </button>
      </div>
    </div>
  );
}
