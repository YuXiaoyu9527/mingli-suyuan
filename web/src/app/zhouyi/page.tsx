"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import BottomNav from "@/components/BottomNav";
import { getApiUrl } from "@/lib/api";
import { Loader2, RefreshCw, Sparkles } from "lucide-react";

// ===== 动画阶段类型 =====
type Stage = "idle" | "spinning" | "forming" | "revealing";

export default function ZhouyiPage() {
  const [question, setQuestion] = useState("我想问事业");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [stage, setStage] = useState<Stage>("idle");
  const [animLines, setAnimLines] = useState<number>(0);
  const [showFlash, setShowFlash] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);

  const handleDivine = async (method = "time") => {
    setLoading(true);
    setStage("spinning");
    setAnimLines(0);
    setShowFlash(false);

    // 并行：动画播放期间同时请求API
    try {
      const resp = await fetch(`${getApiUrl()}/api/zhouyi`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, method }),
      });
      const data = await resp.json();
      setResult(data);
      setHistory([data, ...history].slice(0, 5));
    } catch (e) {
      setLoading(false);
      setStage("idle");
      return;
    }

    // 阶段1 → 2：太极旋转 → 金光一闪 → 成卦
    await new Promise(r => setTimeout(r, 1800));
    setShowFlash(true);
    await new Promise(r => setTimeout(r, 400));
    setShowFlash(false);
    setStage("forming");
    setLoading(false);

    // 阶段2：六条爻线从底部依次砸入
    for (let i = 1; i <= 6; i++) {
      await new Promise(r => setTimeout(r, 180));
      setAnimLines(i);
    }

    // 阶段3：古卷展开
    await new Promise(r => setTimeout(r, 350));
    setStage("revealing");
  };

  const PRESETS = ["我适合换工作吗","这段感情能长久吗","财运何时好转","考试能否顺利","创业前景如何"];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">周易</h1>
        <p className="text-text-secondary text-sm mt-1">六爻起卦 · 梅花易数 · 64卦</p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* 输入区 */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="dao-card space-y-3"
        >
          <input type="text" value={question} onChange={e => setQuestion(e.target.value)}
            placeholder="输入你想问的问题..."
            className="w-full bg-bg-subtle border border-border rounded-lg px-4 py-3 text-text text-sm"/>
          <div className="flex flex-wrap gap-1.5">
            {PRESETS.map(q => (
              <button key={q} onClick={() => setQuestion(q)}
                className={`px-3 py-1 rounded-full text-[11px] tap-active border transition-colors ${question===q?"bg-accent text-white border-accent":"bg-bg-subtle text-text-secondary border-border"}`}>{q}</button>
            ))}
          </div>
          <div className="flex gap-2">
            <button onClick={() => handleDivine("time")} disabled={loading}
              className="flex-1 py-3 rounded-xl text-sm font-medium tap-active flex flex-col items-center gap-1
                bg-accent text-white shadow-lg shadow-accent/20 hover:shadow-accent/30 transition-shadow">
              {loading && stage === "spinning" ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="text-2xl"
                >☯</motion.div>
              ) : "☯"}
              <span>时间起卦</span>
            </button>
            <button onClick={() => handleDivine("random")} disabled={loading}
              className="flex-1 py-3 rounded-xl text-sm font-medium tap-active flex flex-col items-center gap-1
                bg-bg-subtle border border-border text-text hover:border-accent/30 transition-colors">
              {loading && stage === "spinning" ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="text-2xl"
                >☯</motion.div>
              ) : "🎲"}
              <span>随机起卦</span>
            </button>
          </div>
        </motion.div>

        {/* 占卜结果区 */}
        <AnimatePresence mode="wait">
          {result && (
            <div className="space-y-4" key="result-area">
              {/* ========== 卦象核心展示卡 ========== */}
              <div className="relative dao-card-warm text-center py-10 overflow-hidden">
                {/* 金光一闪 */}
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

                <p className="text-text-secondary text-xs mb-4">问：{result.question}</p>

                {/* 六条爻线 — 砸入动画 */}
                <div className="space-y-2.5 mb-6">
                  {(result.display?.lines || []).map((line: any, i: number) => {
                    const visible = i >= (6 - animLines);
                    const isChanging = result.changing_lines?.includes(5 - i);
                    const lineIndex = 5 - i;
                    return (
                      <motion.div
                        key={i}
                        className="flex items-center justify-center gap-3"
                        initial={{ opacity: 0, y: -40, scale: 0.95 }}
                        animate={visible ? {
                          opacity: 1,
                          y: 0,
                          scale: 1,
                          transition: {
                            type: "spring",
                            stiffness: 400,
                            damping: 20,
                            mass: 0.8,
                          }
                        } : {}}
                      >
                        <span className="text-[10px] text-text-tertiary w-8 text-right">
                          {["初","二","三","四","五","上"][lineIndex]}
                        </span>
                        <motion.span
                          className={`text-2xl font-mono tracking-wider ${isChanging ? "text-accent" : "text-text"}`}
                          animate={isChanging && stage === "revealing" ? {
                            boxShadow: [
                              "0 0 0px rgba(196,58,49,0)",
                              "0 0 12px rgba(196,58,49,0.6)",
                              "0 0 0px rgba(196,58,49,0)",
                            ],
                          } : {}}
                          transition={isChanging ? { duration: 2, repeat: Infinity } : {}}
                        >
                          {line.is_yang ? "━━━━━" : "━━ ━━"}
                        </motion.span>
                        {isChanging && stage === "revealing" && (
                          <motion.span
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: "spring", stiffness: 500, damping: 15 }}
                            className="w-5 h-5 rounded-full bg-accent text-white text-[9px] flex items-center justify-center"
                          >变</motion.span>
                        )}
                      </motion.div>
                    );
                  })}
                </div>

                {/* 卦名 — 从模糊到清晰 */}
                <motion.div
                  initial={{ filter: "blur(8px)", opacity: 0 }}
                  animate={stage === "revealing" ? { filter: "blur(0px)", opacity: 1 } : {}}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                >
                  <motion.p
                    initial={{ y: 10 }}
                    animate={stage === "revealing" ? { y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="text-3xl font-[family-name:var(--font-display)] text-text mb-1"
                  >
                    {result.original_name}
                  </motion.p>
                  {result.changing_lines?.length > 0 && (
                    <motion.p
                      initial={{ opacity: 0, x: -8 }}
                      animate={stage === "revealing" ? { opacity: 1, x: 0 } : {}}
                      transition={{ duration: 0.4, delay: 0.25 }}
                      className="text-gold text-sm mb-2"
                    >
                      → {result.changed_name}
                    </motion.p>
                  )}
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={stage === "revealing" ? { opacity: 1 } : {}}
                    transition={{ duration: 0.4, delay: 0.3 }}
                    className="text-text-secondary text-sm"
                  >
                    {result.original_meaning}
                  </motion.p>
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={stage === "revealing" ? { opacity: 1 } : {}}
                    transition={{ duration: 0.4, delay: 0.35 }}
                    className="text-text-tertiary text-xs mt-1"
                  >
                    五行属{result.original_element} · 利{result.direction}方
                  </motion.p>
                </motion.div>
              </div>

              {/* ========== 分析与建议 — 古卷展开 ========== */}
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
                  <motion.div
                    variants={{
                      hidden: { opacity: 0, y: 20, scale: 0.97 },
                      visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
                    }}
                    className="dao-card relative overflow-hidden"
                  >
                    {/* 古卷展开装饰线 */}
                    <div className="absolute top-0 left-4 right-4 h-px bg-gold/30" />
                    <div className="pt-3">
                      <p className="text-xs font-bold text-text mb-2 flex items-center gap-1.5">
                        <Sparkles size={12} className="text-gold"/> 卦象分析
                      </p>
                      <p className="text-sm text-text leading-relaxed">{result.analysis}</p>
                    </div>
                  </motion.div>

                  <motion.div
                    variants={{
                      hidden: { opacity: 0, y: 20, scale: 0.97 },
                      visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
                    }}
                    className="dao-card relative overflow-hidden"
                    style={{
                      borderColor: result.suggestion?.includes("大吉") ? "#4CAF50" :
                                   result.suggestion?.includes("波折") ? "#C0392B" : undefined,
                    }}
                  >
                    <div className="absolute top-0 left-4 right-4 h-px bg-gold/30" />
                    <div className="pt-3">
                      <p className="text-xs font-bold text-text mb-2">建议</p>
                      <p className="text-sm text-text leading-relaxed">{result.suggestion}</p>
                    </div>
                  </motion.div>

                  <motion.div
                    variants={{
                      hidden: { opacity: 0, y: 20, scale: 0.97 },
                      visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
                    }}
                  >
                    <button onClick={() => handleDivine("time")}
                      className="w-full py-2.5 bg-bg-subtle border border-border rounded-lg text-sm text-text-secondary tap-active flex items-center justify-center gap-1 hover:border-gold/30 transition-colors">
                      <RefreshCw size={14}/> 再问一卦
                    </button>
                  </motion.div>

                  {history.length > 1 && (
                    <motion.div
                      variants={{
                        hidden: { opacity: 0, y: 20 },
                        visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
                      }}
                      className="dao-card"
                    >
                      <p className="text-xs font-bold text-text mb-2">占卜记录</p>
                      {history.slice(1).map((h: any, i: number) => (
                        <div key={i} className="flex justify-between py-1.5 border-b border-border last:border-0 text-xs">
                          <span className="text-text-secondary">{h.question}</span>
                          <span className="text-text">{h.original_name}</span>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </motion.div>
              )}
            </div>
          )}
        </AnimatePresence>
      </div>
      <BottomNav/>
    </div>
  );
}
