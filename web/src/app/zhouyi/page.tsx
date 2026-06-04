"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { getApiUrl } from "@/lib/api";
import { Loader2, RefreshCw } from "lucide-react";

export default function ZhouyiPage() {
  const [question, setQuestion] = useState("我想问事业");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [animLines, setAnimLines] = useState<number>(0);
  const [showResult, setShowResult] = useState(false);

  const handleDivine = async (method = "time") => {
    setLoading(true);
    setShowResult(false);
    setAnimLines(0);
    try {
      const resp = await fetch(`${getApiUrl()}/api/zhouyi`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, method }),
      });
      const data = await resp.json();
      setResult(data);
      setHistory([data, ...history].slice(0, 5));

      // 爻线逐条动画
      for (let i = 1; i <= 6; i++) {
        await new Promise(r => setTimeout(r, 200));
        setAnimLines(i);
      }
      // 延迟显示结果
      await new Promise(r => setTimeout(r, 300));
      setShowResult(true);
    } catch (e) { }
    setLoading(false);
  };

  const PRESETS = ["我适合换工作吗","这段感情能长久吗","财运何时好转","考试能否顺利","创业前景如何"];

  const methodBtns = [
    { id: "time", label: "时间起卦", desc: "以当下时间起卦" },
    { id: "random", label: "随机起卦", desc: "随机生成六爻" },
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">周易</h1>
        <p className="text-text-secondary text-sm mt-1">六爻起卦 · 梅花易数 · 64卦</p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* 输入 */}
        <div className="dao-card space-y-3">
          <input type="text" value={question} onChange={e => setQuestion(e.target.value)}
            placeholder="输入你想问的问题..."
            className="w-full bg-bg-subtle border border-border rounded-lg px-4 py-3 text-text text-sm"/>
          <div className="flex flex-wrap gap-1.5">
            {PRESETS.map(q => (
              <button key={q} onClick={() => setQuestion(q)}
                className={`px-3 py-1 rounded-full text-[11px] tap-active border ${question===q?"bg-accent text-white border-accent":"bg-bg-subtle text-text-secondary border-border"}`}>{q}</button>
            ))}
          </div>
          <div className="flex gap-2">
            {methodBtns.map(m => (
              <button key={m.id} onClick={() => handleDivine(m.id)} disabled={loading}
                className="flex-1 py-3 rounded-xl text-sm font-medium tap-active flex flex-col items-center gap-1
                  bg-accent text-white shadow-lg shadow-accent/20">
                {loading ? <Loader2 size={20} className="animate-spin"/> : "☯"}
                <span>{m.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 占卜结果 */}
        {result && (
          <div className="space-y-4">
            {/* 卦象——爻线动画 */}
            <div className="dao-card-warm text-center py-8">
              <p className="text-text-secondary text-xs mb-4">问：{result.question}</p>

              {/* 六条爻线 */}
              <div className="space-y-2.5 mb-6">
                {(result.display?.lines || []).map((line: any, i: number) => {
                  const visible = i >= (6 - animLines);
                  const isChanging = result.changing_lines?.includes(5 - i);
                  const delay = (5 - i) * 0.2;
                  return (
                    <div key={i} className="flex items-center justify-center gap-3"
                      style={{
                        opacity: visible ? 1 : 0,
                        transform: visible ? "translateY(0)" : "translateY(-10px)",
                        transition: `all 0.4s ease ${delay}s`,
                      }}>
                      <span className="text-[10px] text-text-tertiary w-8 text-right">
                        {["初","二","三","四","五","上"][5-i]}
                      </span>
                      <span className={`text-2xl font-mono tracking-wider ${isChanging ? "text-accent" : "text-text"}`}
                        style={isChanging && showResult ? {animation:"pulse 1s infinite"} : {}}>
                        {line.is_yang ? "━━━━━" : "━━ ━━"}
                      </span>
                      {isChanging && showResult && (
                        <span className="w-5 h-5 rounded-full bg-accent text-white text-[9px] flex items-center justify-center"
                          style={{animation:"pulse 1s infinite"}}>变</span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* 卦名 */}
              <div style={{opacity:showResult?1:0,transition:"opacity 0.5s"}}>
                <p className="text-2xl font-[family-name:var(--font-display)] text-text mb-1">
                  {result.original_name}
                </p>
                {result.changing_lines?.length > 0 && (
                  <p className="text-gold text-sm mb-2">→ {result.changed_name}</p>
                )}
                <p className="text-text-secondary text-sm">{result.original_meaning}</p>
                <p className="text-text-tertiary text-xs mt-1">
                  五行属{result.original_element} · 利{result.direction}方
                </p>
              </div>
            </div>

            {/* 分析与建议 */}
            {showResult && (
              <div className="space-y-3 anim-enter">
                <div className="dao-card">
                  <p className="text-xs font-bold text-text mb-2">卦象分析</p>
                  <p className="text-sm text-text leading-relaxed">{result.analysis}</p>
                </div>
                <div className="dao-card"
                  style={{borderColor:result.suggestion?.includes("大吉")?"#4CAF50":result.suggestion?.includes("波折")?"#C0392B":"#E8E8E8"}}>
                  <p className="text-xs font-bold text-text mb-2">建议</p>
                  <p className="text-sm text-text leading-relaxed">{result.suggestion}</p>
                </div>

                <button onClick={()=>handleDivine("time")}
                  className="w-full py-2.5 bg-bg-subtle border border-border rounded-lg text-sm text-text-secondary tap-active flex items-center justify-center gap-1">
                  <RefreshCw size={14}/> 再问一卦
                </button>

                {history.length > 1 && (
                  <div className="dao-card">
                    <p className="text-xs font-bold text-text mb-2">占卜记录</p>
                    {history.slice(1).map((h:any,i:number)=>(
                      <div key={i} className="flex justify-between py-1.5 border-b border-border last:border-0 text-xs">
                        <span className="text-text-secondary">{h.question}</span>
                        <span className="text-text">{h.original_name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      <BottomNav/>
    </div>
  );
}
