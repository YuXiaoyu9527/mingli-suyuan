"use client";

import { useState } from "react";
import BottomNav from "@/components/BottomNav";
import ShareCard from "@/components/ShareCard";
import FeatureGate from "@/components/FeatureGate";
import { Loader2, Heart } from "lucide-react";

type SubTab = "paipan" | "hehun" | "liunian";

export default function MingliPage() {
  const [sub, setSub] = useState<SubTab>("paipan");
  const tabs: {id:SubTab;label:string;icon:string}[] = [
    {id:"paipan",label:"排盘",icon:"☯"},
    {id:"hehun",label:"合婚",icon:"☵"},
    {id:"liunian",label:"流年",icon:"☳"},
  ];

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-3">
        <h1 className="text-2xl text-dao-ink font-[family-name:var(--font-display)] tracking-wider">命理</h1>
        <p className="text-dao-aged text-sm mt-1">排盘 · 合婚 · 流年运势</p>
        {/* 子Tab */}
        <div className="flex gap-1 mt-3 bg-dao-paper-dark rounded-lg p-1">
          {tabs.map(t=>(
            <button key={t.id} onClick={()=>setSub(t.id)}
              className={`flex-1 py-2 rounded-md text-sm transition-colors flex items-center justify-center gap-1
                ${sub===t.id?"bg-dao-paper text-dao-ink font-bold":"text-dao-aged"}`}>
              <span>{t.icon}</span>{t.label}
            </button>
          ))}
        </div>
      </header>

      <div className="px-5 flex-1">
        {sub==="paipan" && <PaipanPanel/>}
        {sub==="hehun" && <HehunPanel/>}
        {sub==="liunian" && <LiunianPanel/>}
      </div>

      <BottomNav/>
    </div>
  );
}

// ===== 排盘子面板 =====
function PaipanPanel() {
  const [form, setForm] = useState({year:1990,month:5,day:20,hour:12,minute:0,gender:"男",city:""});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [tab, setTab] = useState<"overview"|"detail"|"ai">("overview");

  const update = (k:string,v:any)=>setForm({...form,[k]:v});
  const handle = async () => {
    setLoading(true);
    try {
      const r=await fetch("http://localhost:8000/api/full-analysis",{
        method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});
      setResult(await r.json()); setTab("overview");
    }catch(e){}
    setLoading(false);
  };

  const p=result?.paipan?.pillars, g=result?.geju, y=result?.yongshen;

  return (
    <div className="space-y-4 anim-enter">
      <div className="dao-card space-y-3">
        <div className="flex gap-2">
          <input type="number" value={form.year} onChange={e=>update("year",+e.target.value)}
            className="flex-1 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2.5 text-dao-ink text-sm text-center" placeholder="年"/>
          <input type="number" value={form.month} onChange={e=>update("month",+e.target.value)} min={1} max={12}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2.5 text-dao-ink text-sm text-center" placeholder="月"/>
          <input type="number" value={form.day} onChange={e=>update("day",+e.target.value)} min={1} max={31}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2.5 text-dao-ink text-sm text-center" placeholder="日"/>
          <input type="number" value={form.hour} onChange={e=>update("hour",+e.target.value)} min={0} max={23}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2.5 text-dao-ink text-sm text-center" placeholder="时"/>
          <select value={form.gender} onChange={e=>update("gender",e.target.value)}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-1 py-2.5 text-dao-ink text-sm">
            <option>男</option><option>女</option></select>
        </div>
        <div className="flex gap-2">
          <input type="text" value={form.city} onChange={e=>update("city",e.target.value)}
            placeholder="出生城市（可选，真太阳时）"
            className="flex-1 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-3 py-2 text-dao-ink text-xs"/>
          <button onClick={handle} disabled={loading}
            className="bg-dao-red text-white px-5 rounded-lg text-sm font-medium tap-active">
            {loading?<Loader2 size={16} className="animate-spin"/>:"排盘"}
          </button>
        </div>
      </div>

      {result&&p&&(
        <div className="space-y-4 anim-enter">
          <div className="text-center py-6 dao-card">
            <p className="text-[11px] text-dao-aged">{result.paipan.solar_date?.split(" ")[0]}</p>
            <p className="text-sm text-dao-ink mt-0.5">农历{result.paipan.lunar_date}</p>
            {result.true_solar&&<p className="text-[10px] text-dao-gold mt-0.5">真太阳时 {result.true_solar.corrected}</p>}
            <div className="grid grid-cols-4 gap-2 mt-4">
              {["year","month","day","hour"].map((pos,i)=>{
                const gz=p[pos].ganzhi; const isDay=pos==="day";
                return (
                  <div key={pos} className={`${isDay?"ring-2 ring-dao-red/20":""} bg-dao-paper-dark/50 rounded-lg py-3`}>
                    <p className="text-[10px] text-dao-aged">{"年月日时"[i]}柱</p>
                    <p className="text-lg font-[family-name:var(--font-display)] text-dao-ink">{gz[0]}</p>
                    <p className="text-lg font-[family-name:var(--font-display)] text-dao-red">{gz[1]}</p>
                    <p className="text-[9px] text-dao-aged-light">{p[pos].nayin}</p>
                  </div>
                );
              })}
            </div>
            <div className="flex items-center justify-center gap-2 mt-3 flex-wrap text-sm">
              <span className="text-dao-aged">日主</span>
              <span className="text-dao-red font-bold font-[family-name:var(--font-display)]">{result.paipan.rizhu}</span>
              <span className="text-dao-aged-light">({result.paipan.rizhu_wuxing})</span>
              {g&&<span className="text-[10px] text-dao-gold px-2 py-0.5 bg-dao-gold/10 rounded-full">{g.pattern}</span>}
              {y&&<span className="text-[10px] px-2 py-0.5 bg-dao-indigo/10 rounded-full text-dao-indigo-light">{y.wangshuai}</span>}
            </div>
            {y&&(
              <div className="flex items-center justify-center gap-2 mt-2 text-xs">
                <span className="text-dao-aged">用神：</span>
                {(y.recommended||[]).map((wx:string)=><span key={wx} className="text-dao-jade font-medium">{wx}</span>)}
                <span className="text-dao-aged-light">忌：</span>
                {(y.jishen||[]).map((wx:string)=><span key={wx} className="text-dao-red/70">{wx}</span>)}
              </div>
            )}
          </div>

          <div className="flex gap-1 bg-dao-paper-dark rounded-lg p-1">
            {[{id:"overview" as const,label:"概览"},{id:"detail" as const,label:"详情"},{id:"ai" as const,label:"AI"}].map(t=>(
              <button key={t.id} onClick={()=>setTab(t.id)}
                className={`flex-1 py-1.5 rounded-md text-xs ${tab===t.id?"bg-dao-paper font-bold":"text-dao-aged"}`}>{t.label}</button>
            ))}
          </div>

          {tab==="overview"&&(
            <div className="space-y-3 anim-enter">
              {g&&<div className="dao-card py-3 px-4"><p className="text-xs font-bold mb-1">格局</p><p className="text-sm text-dao-ink-light">{g.analysis}</p></div>}
              {y&&<div className="dao-card py-3 px-4"><p className="text-xs font-bold mb-1">用神</p><p className="text-sm text-dao-ink-light">{y.analysis}</p></div>}
              <div className="dao-card py-3 px-4">
                <p className="text-xs font-bold mb-2">五行</p>
                {Object.entries(result.paipan.wuxing_scores as Record<string,number>).map(([wx,score])=>{
                  const cs:Record<string,string>={金:"bg-yellow-500",木:"bg-green-600",水:"bg-blue-500",火:"bg-red-500",土:"bg-amber-600"};
                  const t=Math.max(1,Object.values(result.paipan.wuxing_scores as number[]).reduce((a,b)=>a+b,0));
                  return (
                    <div key={wx} className="flex items-center gap-2 mb-1">
                      <span className="text-[11px] w-4 text-dao-aged">{wx}</span>
                      <div className="flex-1 h-2.5 bg-dao-paper-dark rounded-full overflow-hidden">
                        <div className={`h-full ${cs[wx]||"bg-gray-400"} rounded-full`} style={{width:`${Math.round(score/t*100)}%`}}/>
                      </div>
                      <span className="text-[11px] w-6 text-dao-aged-light text-right">{score}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {tab==="detail"&&(
            <div className="space-y-2 anim-enter text-xs">
              {["year","month","day","hour"].map((pos,i)=>{
                const d=p[pos]; const labels=["年柱","月柱","日柱","时柱"];
                return (
                  <div key={pos} className="dao-card py-2 px-4">
                    <p className="font-bold">{labels[i]} {d.ganzhi} · {d.nayin}</p>
                    <p className="text-dao-aged-light">{d.gan}({d.gan_wuxing}) {d.zhi}({d.zhi_wuxing}) · {pos==="day"?"日主":d.shishen} · {d.changsheng}</p>
                    <p className="text-dao-aged-light">藏干: {d.canggan?.map((c:any)=>`${c.gan}(${c.score})`).join(" ")}</p>
                  </div>
                );
              })}
            </div>
          )}

          {tab==="ai"&&(
            <div className="anim-enter">
              {result.interpretation?(
                <FeatureGate feature="AI简批"><div className="classical-quote text-sm"><p className="text-xs text-dao-aged mb-1">AI简批</p><p className="leading-relaxed whitespace-pre-line">{result.interpretation}</p></div></FeatureGate>
              ):<div className="dao-card text-center py-6"><p className="text-dao-aged text-sm">AI需配置DeepSeek API Key</p></div>}
            </div>
          )}

          <ShareCard ganzhi={[p.year.ganzhi,p.month.ganzhi,p.day.ganzhi,p.hour.ganzhi]}
            rizhu={result.paipan.rizhu} rizhuWuxing={result.paipan.rizhu_wuxing}
            nayin={p.day.nayin} lunarDate={result.paipan.lunar_date}/>
          <p className="text-center text-[10px] text-dao-aged-light">本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义</p>
        </div>
      )}
    </div>
  );
}

// ===== 合婚子面板 =====
function HehunPanel() {
  const [m,setM]=useState({year:1990,month:5,day:20,hour:12});
  const [f,setF]=useState({year:1992,month:8,day:15,hour:10});
  const [load,setLoad]=useState(false);
  const [r,setR]=useState<any>(null);

  const go=async()=>{
    setLoad(true);
    try{
      const resp=await fetch("http://localhost:8000/api/hehun",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({m_year:m.year,m_month:m.month,m_day:m.day,m_hour:m.hour,
                             f_year:f.year,f_month:f.month,f_day:f.day,f_hour:f.hour})});
      setR(await resp.json());
    }catch(e){} setLoad(false);
  };

  return (
    <div className="space-y-4 anim-enter">
      <div className="dao-card space-y-3">
        <p className="text-xs font-bold">男方</p>
        <div className="flex gap-2">
          {["year","month","day","hour"].map(k=>(
            <input key={k} type="number" value={(m as any)[k]} onChange={e=>setM({...m,[k]:+e.target.value})}
              className="flex-1 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-dao-ink text-center"
              placeholder={k==="year"?"年":k==="month"?"月":k==="day"?"日":"时"}/>
          ))}
        </div>
        <p className="text-xs font-bold">女方</p>
        <div className="flex gap-2">
          {["year","month","day","hour"].map(k=>(
            <input key={k} type="number" value={(f as any)[k]} onChange={e=>setF({...f,[k]:+e.target.value})}
              className="flex-1 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-dao-ink text-center"
              placeholder={k==="year"?"年":k==="month"?"月":k==="day"?"日":"时"}/>
          ))}
        </div>
        <button onClick={go} disabled={load}
          className="w-full py-2.5 bg-dao-red text-white rounded-lg text-sm tap-active flex items-center justify-center gap-2">
          {load?<Loader2 size={16} className="animate-spin"/>:<Heart size={16}/>} 开始合婚
        </button>
      </div>

      {r&&(
        <div className="space-y-4 anim-enter">
          <div className="text-center py-6 dao-card">
            <p className="text-dao-aged text-xs">{r.male_bazi}</p>
            <p className="text-dao-aged text-xs mt-1">{r.female_bazi}</p>
            <div className="my-4">
              <span className={`text-4xl font-bold ${r.total_score>=60?"text-dao-jade":r.total_score>=40?"text-dao-gold":"text-dao-red"}`}>{r.total_score}</span>
              <span className="text-dao-aged ml-2">/80</span>
            </div>
            <p className={`text-lg font-bold ${r.total_score>=60?"text-dao-jade":r.total_score>=40?"text-dao-gold":"text-dao-red"}`}>{r.level}</p>
          </div>
          <div className="dao-card">
            {[
              {l:"年柱根基",s:r.nianzhu_score,m:20,d:r.nianzhu_detail},
              {l:"夫妻宫",s:r.rizhi_score,m:30,d:r.rizhi_detail},
              {l:"五行互补",s:r.wuxing_score,m:20,d:r.wuxing_detail},
              {l:"十神匹配",s:r.shishen_score,m:10,d:r.shishen_detail},
            ].map(({l,s,m,d})=>(
              <div key={l} className="mb-3">
                <div className="flex justify-between mb-1"><span className="text-xs">{l}</span><span className="text-[11px] text-dao-gold">{s}/{m}</span></div>
                <div className="h-1.5 bg-dao-paper-dark rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${s>=m*0.7?"bg-dao-jade":s>=0?"bg-dao-gold":"bg-dao-red"}`} style={{width:`${Math.max(0,Math.min(100,(s/m)*100))}%`}}/>
                </div>
                <p className="text-[10px] text-dao-aged-light mt-1">{d}</p>
              </div>
            ))}
          </div>
          <div className="dao-card py-3 px-4"><p className="text-sm text-dao-ink-light leading-relaxed">{r.summary}</p></div>
        </div>
      )}
    </div>
  );
}

// ===== 流年子面板 =====
function LiunianPanel() {
  const [form,setForm]=useState({birth_year:1990,birth_month:5,birth_day:20,birth_hour:12,gender:"男",year:2026});
  const [load,setLoad]=useState(false);
  const [r,setR]=useState<any>(null);

  const go=async()=>{
    setLoad(true);
    try{
      const resp=await fetch("http://localhost:8000/api/liunian",{
        method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});
      setR(await resp.json());
    }catch(e){} setLoad(false);
  };

  return (
    <div className="space-y-4 anim-enter">
      <div className="dao-card space-y-2">
        <div className="flex gap-2">
          <input type="number" value={form.birth_year} onChange={e=>setForm({...form,birth_year:+e.target.value})}
            className="flex-1 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-center" placeholder="出生年"/>
          <input type="number" value={form.birth_month} onChange={e=>setForm({...form,birth_month:+e.target.value})}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-center" placeholder="月"/>
          <input type="number" value={form.birth_day} onChange={e=>setForm({...form,birth_day:+e.target.value})}
            className="w-12 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-center" placeholder="日"/>
          <select value={form.gender} onChange={e=>setForm({...form,gender:e.target.value})}
            className="w-14 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-1 py-2 text-xs"><option>男</option><option>女</option></select>
        </div>
        <div className="flex gap-2 items-center">
          <span className="text-xs text-dao-aged">查流年：</span>
          <input type="number" value={form.year} onChange={e=>setForm({...form,year:+e.target.value})}
            className="w-20 bg-dao-paper-dark border border-dao-paper-darker rounded-lg px-2 py-2 text-xs text-center"/>
          <button onClick={go} disabled={load}
            className="bg-dao-red text-white px-4 py-2 rounded-lg text-xs tap-active ml-auto">{load?<Loader2 size={14} className="animate-spin"/>:"查看"}</button>
        </div>
      </div>

      {r&&r.overall&&(
        <div className="space-y-4 anim-enter">
          <div className="text-center py-6 dao-card">
            <p className="text-dao-aged text-xs">{r.birth_bazi}</p>
            <div className="my-3">
              <span className="text-3xl font-[family-name:var(--font-display)] text-dao-ink">{r.year_ganzhi}</span>
              <span className="text-dao-aged text-sm ml-2">{r.year_shengxiao}年</span>
            </div>
            <p className="text-xs text-dao-gold">{r.shishen}当值 · {r.nayin}</p>
            <p className="text-xs text-dao-aged-light mt-1">{r.shishen_desc}</p>
          </div>
          <div className="dao-card">
            <p className="text-sm text-dao-ink-light leading-relaxed mb-3">{r.overall}</p>
            {[{l:"事业",v:r.career},{l:"财运",v:r.wealth},{l:"健康",v:r.health},{l:"感情",v:r.relationship}].map(({l,v})=>(
              <p key={l} className="text-xs mb-1"><span className="text-dao-aged">{l}：</span><span className="text-dao-ink-light">{v}</span></p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
