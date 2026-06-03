"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { Loader2, Home } from "lucide-react";

export default function FengshuiPage() {
  const [form, setForm] = useState({
    door_direction:"",kitchen:"",bedroom:"",bathroom:"",living_room:"",
    missing_corners:[] as string[], xingsha:[] as string[],
  });
  const [options, setOptions] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(()=>{
    fetch("http://localhost:8000/api/fengshui",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({})})
      .then(r=>r.json()).then(d=>setOptions(d.options)).catch(()=>{});
  },[]);

  const toggle = (arr:string[], item:string) =>
    arr.includes(item) ? arr.filter(x=>x!==item) : [...arr,item];

  const handle = async () => {
    setLoading(true);
    try {
      const r = await fetch("http://localhost:8000/api/fengshui",{
        method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});
      setResult(await r.json());
    }catch(e){} setLoading(false);
  };

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-dao-ink font-[family-name:var(--font-display)] tracking-wider">风水</h1>
        <p className="text-dao-aged text-sm mt-1">八宅 · 九宫飞星 · 形煞 · 缺角</p>
      </header>

      <div className="px-5 flex-1 space-y-4">
        <div className="dao-card space-y-3">
          {/* 大门朝向 */}
          <div>
            <p className="text-xs font-bold text-dao-ink mb-2">大门朝向</p>
            <div className="grid grid-cols-4 gap-1.5">
              {(options?.directions||["北","东北","东","东南","南","西南","西","西北"]).map((d:string)=>(
                <button key={d} onClick={()=>setForm({...form,door_direction:d})}
                  className={`py-2 rounded-lg text-xs tap-active ${form.door_direction===d?"bg-dao-red text-white":"bg-dao-paper-dark text-dao-ink-light border border-dao-paper-darker"}`}>{d}</button>
              ))}
            </div>
          </div>

          {/* 功能区 */}
          <div>
            <p className="text-xs font-bold text-dao-ink mb-2">功能区位置</p>
            {[
              {k:"kitchen" as const,l:"厨房"},
              {k:"bedroom" as const,l:"主卧"},
              {k:"bathroom" as const,l:"卫生间"},
              {k:"living_room" as const,l:"客厅"},
            ].map(({k,l})=>(
              <div key={k} className="flex items-center gap-2 mb-1.5">
                <span className="text-[11px] text-dao-aged w-12">{l}</span>
                <div className="flex gap-1 flex-1">
                  {(options?.directions||["北","东北","东","东南","南","西南","西","西北"]).slice(0,8).map((d:string)=>(
                    <button key={d} onClick={()=>setForm({...form,[k]:d})}
                      className={`flex-1 py-1 rounded text-[10px] tap-active ${(form as any)[k]===d?"bg-dao-gold/20 text-dao-gold-dark border border-dao-gold/50":"bg-dao-paper-dark text-dao-aged-light"}`}>{d}</button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 缺角 */}
          <div>
            <p className="text-xs font-bold text-dao-ink mb-2">缺角（多选）</p>
            <div className="flex flex-wrap gap-1.5">
              {(options?.quejiao_types||["西北","西南","东","东南","北","南","东北","西"]).map((c:string)=>(
                <button key={c} onClick={()=>setForm({...form,missing_corners:toggle(form.missing_corners,c)})}
                  className={`px-3 py-1.5 rounded-full text-[11px] tap-active ${form.missing_corners.includes(c)?"bg-dao-red text-white":"bg-dao-paper-dark text-dao-ink-light border border-dao-paper-darker"}`}>{c}</button>
              ))}
            </div>
          </div>

          {/* 形煞 */}
          <div>
            <p className="text-xs font-bold text-dao-ink mb-2">观察到的形煞（多选）</p>
            <div className="flex flex-wrap gap-1.5">
              {(options?.xingsha_types||["路冲","尖角煞","反弓煞","天斩煞","穿堂煞","门对门"]).map((s:string)=>(
                <button key={s} onClick={()=>setForm({...form,xingsha:toggle(form.xingsha,s)})}
                  className={`px-3 py-1.5 rounded-full text-[11px] tap-active ${form.xingsha.includes(s)?"bg-dao-red text-white":"bg-dao-paper-dark text-dao-ink-light border border-dao-paper-darker"}`}>{s}</button>
              ))}
            </div>
          </div>

          <button onClick={handle} disabled={loading}
            className="w-full py-2.5 bg-dao-red text-white rounded-lg text-sm tap-active flex items-center justify-center gap-2">
            {loading?<Loader2 size={16} className="animate-spin"/>:<Home size={16}/>} 分析风水
          </button>
        </div>

        {result&&(
          <div className="space-y-4 anim-enter">
            {result.house_gua&&(
              <div className="dao-card text-center py-6">
                <p className="text-2xl font-[family-name:var(--font-display)] text-dao-ink">{result.house_gua}宅</p>
                <p className="text-dao-aged text-sm mt-1">{result.house_type}</p>
                <div className="grid grid-cols-2 gap-3 mt-4 text-left text-xs">
                  <div>
                    <p className="text-dao-jade font-bold mb-1">四吉方</p>
                    {result.four_ji?.map((s:string)=><p key={s} className="text-dao-ink-light">· {s}</p>)}
                  </div>
                  <div>
                    <p className="text-dao-red font-bold mb-1">四凶方</p>
                    {result.four_xiong?.map((s:string)=><p key={s} className="text-dao-ink-light">· {s}</p>)}
                  </div>
                </div>
              </div>
            )}

            {result.jiugong_warnings?.length>0&&(
              <div className="dao-card">
                <p className="text-xs font-bold text-dao-ink mb-2">2026九宫飞星</p>
                {result.jiugong_warnings.map((w:string)=><p key={w} className="text-[11px] text-dao-ink-light mb-1">{w}</p>)}
              </div>
            )}

            {result.xingsha_advice?.length>0&&(
              <div className="dao-card">
                <p className="text-xs font-bold text-dao-ink mb-2">形煞化解</p>
                {result.xingsha_advice.map((a:string)=><p key={a} className="text-[11px] text-dao-ink-light mb-1">{a}</p>)}
              </div>
            )}

            {result.quejiao_advice?.length>0&&(
              <div className="dao-card">
                <p className="text-xs font-bold text-dao-ink mb-2">缺角补救</p>
                {result.quejiao_advice.map((a:string)=><p key={a} className="text-[11px] text-dao-ink-light mb-1">{a}</p>)}
              </div>
            )}

            {result.room_advice?.length>0&&(
              <div className="dao-card">
                <p className="text-xs font-bold text-dao-ink mb-2">布局建议</p>
                {result.room_advice.map((a:string)=><p key={a} className="text-[11px] text-dao-ink-light mb-1">{a}</p>)}
              </div>
            )}

            <p className="text-center text-[10px] text-dao-aged-light">本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义</p>
          </div>
        )}
      </div>
      <BottomNav/>
    </div>
  );
}
