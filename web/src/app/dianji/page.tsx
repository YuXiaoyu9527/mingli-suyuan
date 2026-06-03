"use client";

import { useState, useEffect } from "react";
import { getApiUrl } from "@/lib/api";
import BottomNav from "@/components/BottomNav";
import { Search, Star, Loader2, BookOpen } from "lucide-react";

type SubTab = "search" | "mingli";

export default function DianjiPage() {
  const [sub, setSub] = useState<SubTab>("search");

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-3">
        <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider">典籍</h1>
        <p className="text-text-secondary text-sm mt-1">古籍检索 · 历史命例</p>
        <div className="flex gap-1 mt-3 bg-bg-subtle rounded-lg p-1">
          {[
            {id:"search" as const,label:"古籍检索",icon:"📜"},
            {id:"mingli" as const,label:"历史命例",icon:"👤"},
          ].map(t=>(
            <button key={t.id} onClick={()=>setSub(t.id)}
              className={`flex-1 py-2 rounded-md text-sm transition-colors flex items-center justify-center gap-1
                ${sub===t.id?"bg-bg text-text font-bold":"text-text-secondary"}`}>
              {t.icon} {t.label}
            </button>
          ))}
        </div>
      </header>

      <div className="px-5 flex-1">
        {sub==="search" && <SearchPanel/>}
        {sub==="mingli" && <MingliPanel/>}
      </div>
      <BottomNav/>
    </div>
  );
}

// 古籍检索
function SearchPanel() {
  const [q,setQ]=useState("");
  const [res,setRes]=useState<any[]>([]);
  const [load,setLoad]=useState(false);

  const go = async (query?: string) => {
    const sq = query || q; if(!sq.trim()) return;
    setLoad(true);
    try {
      const r = await fetch(`${getApiUrl()}/api/search`,{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({query:sq,top_k:10})});
      const d = await r.json(); setRes(d.results||[]);
    }catch(e){} setLoad(false);
  };

  return (
    <div className="space-y-3 anim-enter">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary"/>
          <input type="text" value={q} onChange={e=>setQ(e.target.value)}
            onKeyDown={e=>e.key==="Enter"&&go()}
            placeholder="搜索关键词：格局/神煞/干支…"
            className="w-full bg-bg-subtle border border-border rounded-lg pl-9 pr-3 py-2.5 text-text text-sm"/>
        </div>
        <button onClick={()=>go()} disabled={load}
          className="bg-accent text-white px-4 rounded-lg tap-active text-xs">{load?<Loader2 size={16} className="animate-spin"/>:"搜索"}</button>
      </div>

      {res.length===0&&!load&&!q&&(
        <div className="text-center py-8">
          <p className="text-xs text-text-secondary mb-3">热门搜索</p>
          <div className="grid grid-cols-2 gap-2 max-w-xs mx-auto">
            {[
              {q:"正官格",icon:"官"},{q:"七杀格",icon:"杀"},
              {q:"五行相生相克",icon:"行"},{q:"天乙贵人",icon:"贵"},
              {q:"桃花咸池",icon:"桃"},{q:"嫁娶吉日",icon:"嫁"},
              {q:"建除十二神",icon:"建"},{q:"纳音取象",icon:"音"},
            ].map(({q,icon})=>(
              <button key={q} onClick={()=>{setQ(q);go(q);}}
                className="flex items-center gap-2 px-3 py-2 bg-bg-subtle rounded-lg text-xs text-text tap-active border border-border text-left">
                <span className="jing-seal flex-shrink-0">{icon}</span>{q}
              </button>
            ))}
          </div>
        </div>
      )}

      {res.map((r:any,i:number)=>(
        <div key={i} className="dao-card py-3 px-4">
          <div className="flex items-start justify-between mb-1">
            <span className="text-xs font-bold text-accent font-[family-name:var(--font-display)]">{r.source_name}</span>
            <span className="text-[11px] text-gold">{Math.round(r.score*100)}%</span>
          </div>
          <p className="text-[11px] text-text-secondary mb-1">{r.volume} · {r.section}</p>
          <p className="text-xs text-text leading-relaxed line-clamp-4">{r.content}</p>
          <div className="flex gap-1 mt-1.5">
            {(r.tags||[]).filter((t:string)=>t!=="其他").slice(0,4).map((t:string)=>
              <span key={t} className="text-[10px] px-1.5 py-0.5 bg-gold/10 text-text-secondary rounded">{t}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// 历史命例
function MingliPanel() {
  const [cases,setCases]=useState<any[]>([]);
  const [patterns,setPatterns]=useState<any[]>([]);
  const [load,setLoad]=useState(true);
  const [pat,setPat]=useState("");
  const [sel,setSel]=useState<any>(null);

  const go = async (p?:string) => {
    setLoad(true);
    try {
      const r = await fetch(`${getApiUrl()}/api/mingli`,{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({pattern:p||null})});
      const d = await r.json();
      setCases(d.cases||[]); setPatterns(d.patterns||[]);
    }catch(e){} setLoad(false);
  };

  useEffect(()=>{go()},[]);

  return (
    <div className="space-y-3 anim-enter">
      <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
        <button onClick={()=>{setPat("");go();}}
          className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs border tap-active ${!pat?"bg-accent text-white border-accent":"bg-bg-subtle text-text border-border"}`}>全部</button>
        {patterns.slice(0,8).map(({name,count}:any)=>(
          <button key={name} onClick={()=>{setPat(name);go(name);}}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs border tap-active ${pat===name?"bg-gold/20 text-gold-dark border-gold/50":"bg-bg-subtle text-text border-border"}`}>{name}({count})</button>
        ))}
      </div>

      {load&&<Loader2 size={20} className="animate-spin text-gold mx-auto mt-8"/>}

      {cases.map((c:any)=>(
        <div key={c.id} className="dao-card py-3 px-4 tap-active" onClick={()=>setSel(c)}>
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-bold font-[family-name:var(--font-display)]">{c.name}</h3>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[11px] text-text-secondary">{c.era}</span>
                <span className="text-[11px] font-mono text-text">{c.bazi}</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="px-2 py-0.5 bg-accent/10 text-accent text-[10px] rounded-full">{c.pattern}</span>
              <span className="flex items-center gap-1 text-[10px] text-text-secondary">
                <Star size={9} className={c.reliability==="正史记载"?"fill-dao-gold text-gold":"text-text-tertiary"}/> {c.reliability}
              </span>
            </div>
          </div>
          <p className="text-[11px] text-text leading-relaxed line-clamp-2 mt-2">{c.commentary}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-text-tertiary">{c.source}</span>
            <div className="flex gap-1">{(c.tags||[]).slice(0,3).map((t:string)=>
              <span key={t} className="text-[9px] px-1.5 py-0.5 bg-bg-subtle text-text-secondary rounded">{t}</span>
            )}</div>
          </div>
        </div>
      ))}

      {sel&&(
        <div className="fixed inset-0 z-[60] flex items-end justify-center bg-dao-ink/40 backdrop-blur-sm" onClick={()=>setSel(null)}>
          <div className="w-full max-w-[430px] bg-bg rounded-t-2xl p-6 max-h-[70vh] overflow-y-auto anim-enter" onClick={e=>e.stopPropagation()}>
            <div className="flex items-start justify-between mb-4">
              <div><h2 className="text-xl font-[family-name:var(--font-display)]">{sel.name}</h2><p className="text-xs text-text-secondary">{sel.era} · {sel.pattern} · {sel.rishu}日主</p></div>
              <button onClick={()=>setSel(null)} className="text-text-secondary text-xl">&times;</button>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center mb-4">
              {sel.bazi.split(" ").map((gz:string,i:number)=>{
                const labels=["年柱","月柱","日柱","时柱"];
                return (
                  <div key={i} className="bg-bg-subtle/50 rounded-lg py-3">
                    <p className="text-[9px] text-text-secondary">{labels[i]}</p>
                    <p className="text-base font-[family-name:var(--font-display)] text-text">{gz[0]}</p>
                    <p className="text-base font-[family-name:var(--font-display)] text-accent">{gz[1]}</p>
                  </div>
                );
              })}
            </div>
            <div className="classical-quote text-sm mb-3">{sel.commentary}</div>
            <div className="flex items-center gap-4 text-xs text-text-secondary">
              <span>{sel.source}</span>
              <span className="flex items-center gap-1"><Star size={10} className={sel.reliability==="正史记载"?"fill-dao-gold text-gold":""}/>{sel.reliability}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
