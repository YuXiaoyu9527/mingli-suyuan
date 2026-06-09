"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import BottomNav from "@/components/BottomNav";
import { getApiUrl } from "@/lib/api";
import { RefreshCw, Sparkles, Clock, Shuffle, Shirt, MapPin, Lightbulb } from "lucide-react";

type Stage = "idle" | "spinning" | "forming" | "revealing";
type Method = "time" | "random" | null;

export default function ZhouyiPage() {
  const [question, setQuestion] = useState("");
  const [selectedMethod, setSelectedMethod] = useState<Method>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [stage, setStage] = useState<Stage>("idle");
  const [animLines, setAnimLines] = useState<number>(0);
  const [showFlash, setShowFlash] = useState(false);

  const handleDivine = async () => {
    if (!selectedMethod || !question.trim()) return;
    const method = selectedMethod;
    setLoading(true);
    setStage("spinning");
    setAnimLines(0);
    setShowFlash(false);

    try {
      const resp = await fetch(`${getApiUrl()}/api/zhouyi`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), method }),
      });
      const data = await resp.json();
      setResult(data);
      setHistory([data, ...history].slice(0, 5));
    } catch {
      setLoading(false);
      setStage("idle");
      return;
    }

    // 太极旋转 → 金光一闪
    await new Promise((r) => setTimeout(r, 1800));
    setShowFlash(true);
    await new Promise((r) => setTimeout(r, 400));
    setShowFlash(false);
    setStage("forming");
    setLoading(false);

    // 六条爻线依次砸入
    for (let i = 1; i <= 6; i++) {
      await new Promise((r) => setTimeout(r, 180));
      setAnimLines(i);
    }

    // 古卷展开
    await new Promise((r) => setTimeout(r, 350));
    setStage("revealing");
  };

  /** 重置，方便再问 */
  const reset = () => {
    setSelectedMethod(null);
    setResult(null);
    setStage("idle");
    setAnimLines(0);
  };

  const PRESETS = [
    "我适合换工作吗",
    "这段感情能长久吗",
    "财运何时好转",
    "8月份能成单吗",
    "创业前景如何",
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">
          周易
        </h1>
        <p className="text-text-secondary text-sm mt-1">
          六爻起卦 · 梅花易数 · 五行调和
        </p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* ===== 输入区 ===== */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="dao-card space-y-3"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="输入你想问的问题（如：我8月份能成单吗）"
            className="w-full bg-bg-subtle border border-border rounded-lg px-4 py-3
                       text-text text-sm focus:outline-none focus:border-gold
                       placeholder:text-text-tertiary/60"
          />
          {/* 预设问题 */}
          <div className="flex flex-wrap gap-1.5">
            {PRESETS.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className={`px-3 py-1 rounded-full text-[11px] tap-active border transition-colors ${
                  question === q
                    ? "bg-accent text-white border-accent"
                    : "bg-bg-subtle text-text-secondary border-border"
                }`}
              >
                {q}
              </button>
            ))}
          </div>

          {/* 起卦方式选择 — 两种卡片 */}
          <p className="text-[10px] text-text-tertiary tracking-wider text-center">
            — 选择起卦方式 —
          </p>
          <div className="grid grid-cols-2 gap-3">
            {/* 时间起卦 */}
            <button
              onClick={() => setSelectedMethod("time")}
              className={`p-4 rounded-xl border-2 text-left tap-active transition-all ${
                selectedMethod === "time"
                  ? "border-accent bg-accent/5 shadow-sm"
                  : "border-border bg-bg-subtle hover:border-gold/30"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    selectedMethod === "time"
                      ? "bg-accent text-white"
                      : "bg-bg text-text-secondary"
                  }`}
                >
                  <Clock size={16} />
                </div>
                <span className="text-sm font-bold text-text">时间起卦</span>
              </div>
              <p className="text-[10px] text-text-tertiary leading-relaxed">
                以当前年月日时数字起卦，含体用生克分析。与天时相应，适合问时机类问题。
              </p>
            </button>

            {/* 随机起卦 */}
            <button
              onClick={() => setSelectedMethod("random")}
              className={`p-4 rounded-xl border-2 text-left tap-active transition-all ${
                selectedMethod === "random"
                  ? "border-gold bg-gold/5 shadow-sm"
                  : "border-border bg-bg-subtle hover:border-gold/30"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    selectedMethod === "random"
                      ? "bg-gold text-white"
                      : "bg-bg text-text-secondary"
                  }`}
                >
                  <Shuffle size={16} />
                </div>
                <span className="text-sm font-bold text-text">随机起卦</span>
              </div>
              <p className="text-[10px] text-text-tertiary leading-relaxed">
                心诚则灵，系统随机模拟三枚铜钱投六次。适合问运势、决策类问题。
              </p>
            </button>
          </div>

          {/* 起卦按钮 */}
          <button
            onClick={handleDivine}
            disabled={loading || !selectedMethod || !question.trim()}
            className="w-full py-3 rounded-xl text-sm font-medium tap-active transition-all
                       flex items-center justify-center gap-2
                       bg-accent text-white shadow-lg shadow-accent/20
                       disabled:bg-bg-subtle disabled:text-text-tertiary disabled:shadow-none
                       hover:shadow-accent/30"
          >
            {loading && stage === "spinning" ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                className="text-xl"
              >
                ☯
              </motion.div>
            ) : (
              "☯ 开始起卦"
            )}
          </button>
        </motion.div>

        {/* ===== 占卜结果区 ===== */}
        <AnimatePresence mode="wait">
          {result && (
            <div className="space-y-4" key="result-area">
              {/* === 卦象核心展示卡 === */}
              <div className="relative dao-card-warm text-center py-10 overflow-hidden">
                <AnimatePresence>
                  {showFlash && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: [0, 1, 0.8, 0] }}
                      transition={{ duration: 0.5, times: [0, 0.1, 0.3, 1] }}
                      className="absolute inset-0 bg-gold/30 pointer-events-none z-10"
                    />
                  )}
                </AnimatePresence>

                <p className="text-text-secondary text-xs mb-4">
                  问：{result.question}
                </p>

                {/* 六条爻线 */}
                <div className="space-y-2.5 mb-6">
                  {(result.display?.lines || []).map((line: any, i: number) => {
                    const visible = i >= 6 - animLines;
                    const isChanging = result.changing_lines?.includes(5 - i);
                    const lineIndex = 5 - i;
                    return (
                      <motion.div
                        key={i}
                        className="flex items-center justify-center gap-3"
                        initial={{ opacity: 0, y: -40, scale: 0.95 }}
                        animate={
                          visible
                            ? {
                                opacity: 1,
                                y: 0,
                                scale: 1,
                                transition: {
                                  type: "spring",
                                  stiffness: 400,
                                  damping: 20,
                                  mass: 0.8,
                                },
                              }
                            : {}
                        }
                      >
                        <span className="text-[10px] text-text-tertiary w-8 text-right">
                          {["初", "二", "三", "四", "五", "上"][lineIndex]}
                        </span>
                        <motion.span
                          className={`text-2xl font-mono tracking-wider ${
                            isChanging ? "text-accent" : "text-text"
                          }`}
                          animate={
                            isChanging && stage === "revealing"
                              ? {
                                  boxShadow: [
                                    "0 0 0px rgba(196,58,49,0)",
                                    "0 0 12px rgba(196,58,49,0.6)",
                                    "0 0 0px rgba(196,58,49,0)",
                                  ],
                                }
                              : {}
                          }
                          transition={
                            isChanging
                              ? { duration: 2, repeat: Infinity }
                              : {}
                          }
                        >
                          {line.is_yang ? "━━━━━" : "━━ ━━"}
                        </motion.span>
                        {isChanging && stage === "revealing" && (
                          <motion.span
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{
                              type: "spring",
                              stiffness: 500,
                              damping: 15,
                            }}
                            className="w-5 h-5 rounded-full bg-accent text-white text-[9px]
                                       flex items-center justify-center"
                          >
                            变
                          </motion.span>
                        )}
                      </motion.div>
                    );
                  })}
                </div>

                {/* 卦名 */}
                <motion.div
                  initial={{ filter: "blur(8px)", opacity: 0 }}
                  animate={
                    stage === "revealing"
                      ? { filter: "blur(0px)", opacity: 1 }
                      : {}
                  }
                  transition={{ duration: 0.6, ease: "easeOut" }}
                >
                  <p className="text-3xl font-[family-name:var(--font-display)] text-text mb-1">
                    {result.original_name}
                  </p>
                  {result.changing_lines?.length > 0 && (
                    <p className="text-gold text-sm mb-2">
                      → {result.changed_name}
                    </p>
                  )}
                  <p className="text-text-secondary text-sm">
                    {result.original_meaning}
                  </p>
                  <p className="text-text-tertiary text-xs mt-1">
                    五行属{result.original_element} · 利{result.direction}方
                  </p>
                </motion.div>
              </div>

              {/* === 分层分析卡片 === */}
              {stage === "revealing" && (
                <motion.div
                  className="space-y-3"
                  initial="hidden"
                  animate="visible"
                  variants={{
                    hidden: {},
                    visible: { transition: { staggerChildren: 0.12 } },
                  }}
                >
                  {/* 1. 卦象解读 */}
                  <motion.div
                    variants={cardVariant}
                    className="dao-card relative overflow-hidden"
                  >
                    <div className="absolute top-0 left-4 right-4 h-px bg-gold/30" />
                    <div className="pt-3">
                      <p className="text-xs font-bold text-text mb-2 flex items-center gap-1.5">
                        <Sparkles size={12} className="text-gold" /> 卦象解读
                      </p>
                      <p className="text-sm text-text leading-relaxed whitespace-pre-line">
                        {result.analysis}
                      </p>
                    </div>
                  </motion.div>

                  {/* 2. 行动建议 */}
                  <motion.div
                    variants={cardVariant}
                    className="dao-card relative overflow-hidden"
                  >
                    <div className="absolute top-0 left-4 right-4 h-px bg-accent/30" />
                    <div className="pt-3">
                      <p className="text-xs font-bold text-text mb-2 flex items-center gap-1.5">
                        <Lightbulb size={12} className="text-accent" /> 行动建议
                      </p>
                      <p className="text-sm text-text leading-relaxed whitespace-pre-line">
                        {result.suggestion}
                      </p>
                    </div>
                  </motion.div>

                  {/* 3. 五行调和 — 具体举措 */}
                  {result.wuxing_advice && (
                    <motion.div
                      variants={cardVariant}
                      className="dao-card relative overflow-hidden border-gold/20"
                      style={{ borderColor: "rgba(201,169,110,0.25)" }}
                    >
                      <div className="absolute top-0 left-4 right-4 h-px bg-gold/30" />
                      <div className="pt-3 space-y-3">
                        <p className="text-xs font-bold text-text flex items-center gap-1.5">
                          <Shirt size={12} className="text-gold" /> 五行调和 · 具体举措
                        </p>

                        {/* 调和原理 */}
                        {result.wuxing_advice.tension_note && (
                          <div className="bg-bg-subtle rounded-lg p-3">
                            <p className="text-[11px] text-text-secondary leading-relaxed">
                              ⚠️ {result.wuxing_advice.tension_note}
                            </p>
                          </div>
                        )}

                        <div className="grid grid-cols-1 gap-2">
                          {/* 穿衣颜色 */}
                          <div className="flex items-start gap-2 bg-bg-subtle rounded-lg p-3">
                            <span className="text-base flex-shrink-0">👔</span>
                            <div>
                              <p className="text-xs font-medium text-text">
                                穿衣颜色
                              </p>
                              <p className="text-[11px] text-text-secondary mt-0.5">
                                {(result.wuxing_advice.colors || [])
                                  .map((c: string) => `${c}色`)
                                  .join("、")}
                              </p>
                            </div>
                          </div>

                          {/* 随身物品 */}
                          <div className="flex items-start gap-2 bg-bg-subtle rounded-lg p-3">
                            <span className="text-base flex-shrink-0">🎒</span>
                            <div>
                              <p className="text-xs font-medium text-text">
                                随身物品
                              </p>
                              <p className="text-[11px] text-text-secondary mt-0.5">
                                {(result.wuxing_advice.items || []).join(
                                  " · "
                                )}
                              </p>
                            </div>
                          </div>

                          {/* 具体行动 */}
                          <div className="flex items-start gap-2 bg-bg-subtle rounded-lg p-3">
                            <span className="text-base flex-shrink-0">🧭</span>
                            <div>
                              <p className="text-xs font-medium text-text">
                                具体行动
                              </p>
                              <p className="text-[11px] text-text-secondary mt-0.5">
                                {(result.wuxing_advice.actions || []).join(
                                  " · "
                                )}
                              </p>
                            </div>
                          </div>

                          {/* 有利方位 */}
                          <div className="flex items-start gap-2 bg-bg-subtle rounded-lg p-3">
                            <MapPin size={14} className="text-text-tertiary flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="text-xs font-medium text-text">
                                有利方位
                              </p>
                              <p className="text-[11px] text-text-secondary mt-0.5">
                                {result.wuxing_advice.direction || result.direction}
                                方
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* 再问一卦 */}
                  <motion.div variants={cardVariant}>
                    <button
                      onClick={reset}
                      className="w-full py-2.5 bg-bg-subtle border border-border rounded-lg
                                 text-sm text-text-secondary tap-active flex items-center
                                 justify-center gap-1 hover:border-gold/30 transition-colors"
                    >
                      <RefreshCw size={14} /> 再问一卦
                    </button>
                  </motion.div>

                  {/* 占卜记录 */}
                  {history.length > 1 && (
                    <motion.div variants={cardVariant} className="dao-card">
                      <p className="text-xs font-bold text-text mb-2">
                        占卜记录
                      </p>
                      {history.slice(1).map((h: any, i: number) => (
                        <div
                          key={i}
                          className="flex justify-between py-1.5 border-b border-border last:border-0 text-xs"
                        >
                          <span className="text-text-secondary truncate mr-2 max-w-[60%]">
                            {h.question}
                          </span>
                          <span className="text-text flex-shrink-0">
                            {h.original_name}
                          </span>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* 免责 */}
              <p className="text-center text-[10px] text-text-tertiary pb-2">
                本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不代表专业建议
              </p>
            </div>
          )}
        </AnimatePresence>
      </div>
      <BottomNav />
    </div>
  );
}

const cardVariant = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] as const },
  },
};
