"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import { getApiUrl } from "@/lib/api";
import { Loader2, RefreshCw } from "lucide-react";

export default function ZhouyiPage() {
  const [question, setQuestion] = useState("我想问事业");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  const handleDivine = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${getApiUrl()}/api/zhouyi`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await resp.json();
      setResult(data);
      setHistory([data, ...history].slice(0, 5));
    } catch (e) { }
    setLoading(false);
  };

  const PRESET_QUESTIONS = [
    "我今年适合换工作吗",
    "这段感情能长久吗",
    "财运什么时候好转",
    "考试能否顺利",
    "创业前景如何",
    "健康方面需要注意什么",
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">周易</h1>
        <p className="text-text-secondary text-sm mt-1">六爻起卦 · 64卦 · 变爻变卦</p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* 输入问题 */}
        <div className="dao-card space-y-3">
          <input
            type="text" value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="输入你想问的问题..."
            className="w-full bg-bg-subtle border border-border rounded-lg px-4 py-3 text-text text-sm"
          />
          <div className="flex flex-wrap gap-1.5">
            {PRESET_QUESTIONS.map(q => (
              <button key={q} onClick={() => setQuestion(q)}
                className={`px-3 py-1 rounded-full text-[11px] tap-active border transition-colors
                  ${question === q ? "bg-accent text-white border-accent" : "bg-bg-subtle text-text-secondary border-border"}`}>
                {q}
              </button>
            ))}
          </div>
          <button onClick={handleDivine} disabled={loading}
            className="w-full py-4 bg-accent text-white rounded-xl text-base font-medium tap-active flex items-center justify-center gap-2 shadow-lg shadow-accent/20">
            {loading ? <Loader2 size={22} className="animate-spin" /> : "☯"}
            {loading ? "起卦中..." : "开始占卜"}
          </button>
        </div>

        {/* 占卜结果 */}
        {result && (
          <div className="space-y-4 anim-enter">
            {/* 卦象卡片 */}
            <div className="text-center py-6 rounded-xl"
              style={{ background: "linear-gradient(135deg,#FFFBF0 0%,#FFF8E7 100%)", border: "1px solid #E8D5A3" }}>
              <p className="text-text-secondary text-xs mb-3">问：{result.question}</p>

              {/* 卦象展示 */}
              <div className="space-y-2 mb-4">
                {(result.display?.lines || []).map((line: any, i: number) => (
                  <div key={i} className="flex items-center justify-center gap-3">
                    <span className="text-[10px] text-text-tertiary w-8 text-right">{line.position}</span>
                    <span className={`text-xl font-mono ${line.is_yang ? "text-text" : "text-text-secondary"}`}>
                      {line.is_yang ? "━━━━━" : "━━ ━━"}
                    </span>
                    {result.changing_lines?.includes(5 - i) && (
                      <span className="w-4 h-4 rounded-full bg-accent text-white text-[9px] flex items-center justify-center">变</span>
                    )}
                  </div>
                ))}
              </div>

              {/* 卦名 */}
              <p className="text-2xl font-[family-name:var(--font-display)] text-text mb-1">{result.original_name}</p>
              {result.changing_lines?.length > 0 && (
                <p className="text-gold text-sm mb-1">→ {result.changed_name}</p>
              )}
              <p className="text-text-secondary text-sm">{result.original_meaning}</p>
              <p className="text-text-tertiary text-xs mt-1">五行属{result.original_element} · 利{result.direction}方</p>
            </div>

            {/* 分析与建议 */}
            <div className="dao-card">
              <p className="text-xs font-bold text-text mb-2">卦象分析</p>
              <p className="text-sm text-text leading-relaxed">{result.analysis}</p>
            </div>
            <div className="dao-card"
              style={{ borderColor: result.suggestion?.includes("大吉") ? "#4CAF50" : result.suggestion?.includes("波折") ? "#C0392B" : "#E8E8E8" }}>
              <p className="text-xs font-bold text-text mb-2">建议</p>
              <p className="text-sm text-text leading-relaxed">{result.suggestion}</p>
            </div>

            {/* 再问一卦 */}
            <button onClick={handleDivine}
              className="w-full py-2.5 bg-bg-subtle border border-border rounded-lg text-sm text-text-secondary tap-active flex items-center justify-center gap-1">
              <RefreshCw size={14} /> 再问一卦
            </button>

            {/* 历史 */}
            {history.length > 1 && (
              <div className="dao-card">
                <p className="text-xs font-bold text-text mb-2">占卜记录</p>
                {history.slice(1).map((h: any, i: number) => (
                  <div key={i} className="flex items-center justify-between py-1.5 border-b border-border last:border-0 text-xs">
                    <span className="text-text-secondary">{h.question}</span>
                    <span className="text-text">{h.original_name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  );
}
