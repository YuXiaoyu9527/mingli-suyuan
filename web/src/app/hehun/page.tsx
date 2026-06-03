"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import { Loader2, Heart } from "lucide-react";

export default function HehunPage() {
  const [m, setM] = useState({ year:1990,month:5,day:20,hour:12 });
  const [f, setF] = useState({ year:1992,month:8,day:15,hour:10 });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const resp = await fetch("http://localhost:8000/api/hehun", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          m_year:m.year,m_month:m.month,m_day:m.day,m_hour:m.hour,
          f_year:f.year,f_month:f.month,f_day:f.day,f_hour:f.hour,
        }),
      });
      setResult(await resp.json());
    } catch(e){}
    setLoading(false);
  };

  const ScoreBar = ({ label, score, max, detail }: {label:string,score:number,max:number,detail:string}) => (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-text">{label}</span>
        <span className="text-[11px] text-gold">{score}/{max}</span>
      </div>
      <div className="h-1.5 bg-bg-subtle rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${score>=max*0.7?"bg-green":score>=0?"bg-gold":"bg-accent"}`}
          style={{width:`${Math.max(0,Math.min(100,(score/max)*100))}%`}}/>
      </div>
      <p className="text-[10px] text-text-tertiary mt-1">{detail}</p>
    </div>
  );

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">八字合婚</h1>
        <p className="text-text-secondary text-sm mt-1">年柱根基 · 夫妻宫 · 五行互补 · 十神匹配</p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        {/* 输入 */}
        <div className="dao-card space-y-3">
          <p className="text-xs font-bold text-text">男方</p>
          <div className="flex gap-2">
            <input type="number" value={m.year} onChange={e=>setM({...m,year:+e.target.value})}
              className="flex-1 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="年"/>
            <input type="number" value={m.month} onChange={e=>setM({...m,month:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="月"/>
            <input type="number" value={m.day} onChange={e=>setM({...m,day:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="日"/>
            <input type="number" value={m.hour} onChange={e=>setM({...m,hour:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="时"/>
          </div>
          <p className="text-xs font-bold text-text">女方</p>
          <div className="flex gap-2">
            <input type="number" value={f.year} onChange={e=>setF({...f,year:+e.target.value})}
              className="flex-1 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="年"/>
            <input type="number" value={f.month} onChange={e=>setF({...f,month:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="月"/>
            <input type="number" value={f.day} onChange={e=>setF({...f,day:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="日"/>
            <input type="number" value={f.hour} onChange={e=>setF({...f,hour:+e.target.value})}
              className="w-12 bg-bg-subtle border border-border rounded-lg px-2 py-2 text-text text-xs" placeholder="时"/>
          </div>
          <button onClick={handleSubmit} disabled={loading}
            className="w-full py-2.5 bg-accent text-white rounded-lg text-sm font-medium tap-active flex items-center justify-center gap-1.5">
            {loading ? <Loader2 size={16} className="animate-spin"/> : <Heart size={16}/>}
            {loading ? "分析中..." : "开始合婚"}
          </button>
        </div>

        {/* 结果 */}
        {result && (
          <div className="space-y-4 anim-enter">
            {/* 总分 */}
            <div className="text-center py-6 dao-card">
              <p className="text-text-secondary text-xs">{result.male_bazi}</p>
              <p className="text-text-secondary text-xs mt-1">{result.female_bazi}</p>
              <div className="my-4">
                <span className={`text-4xl font-bold ${result.total_score>=60?"text-green":result.total_score>=40?"text-gold":"text-accent"}`}>
                  {result.total_score}
                </span>
                <span className="text-text-secondary ml-2">/ 80</span>
              </div>
              <p className={`text-lg font-bold ${result.total_score>=60?"text-green":result.total_score>=40?"text-gold":"text-accent"}`}>
                {result.level}
              </p>
            </div>

            {/* 四维度评分 */}
            <div className="dao-card">
              <h3 className="text-sm font-bold text-text mb-3">四维分析</h3>
              <ScoreBar label="年柱根基" score={result.nianzhu_score} max={20} detail={result.nianzhu_detail}/>
              <ScoreBar label="夫妻宫" score={result.rizhi_score} max={30} detail={result.rizhi_detail}/>
              <ScoreBar label="五行互补" score={result.wuxing_score} max={20} detail={result.wuxing_detail}/>
              <ScoreBar label="十神匹配" score={result.shishen_score} max={10} detail={result.shishen_detail}/>
            </div>

            {/* 总结 */}
            <div className="dao-card">
              <h3 className="text-sm font-bold text-text mb-2">综合评语</h3>
              <p className="text-sm text-text leading-relaxed">{result.summary}</p>
            </div>

            <p className="text-center text-[10px] text-text-tertiary pb-4">
              本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义
            </p>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
