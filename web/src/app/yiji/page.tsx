"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { getYiji, searchZeji, YijiParams } from "@/lib/api";
import { Loader2, RefreshCw, Star, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

const COLOR_MAP: Record<string, string> = {
  "红色":"#C41E3A","紫色":"#7B2D8E","橙色":"#E8651A","绿色":"#2E7D32",
  "青色":"#00897B","黄色":"#F9A825","棕色":"#795548","白色":"#E0E0E0",
  "金色":"#FFD54F","银色":"#BDBDBD","黑色":"#212121","深蓝":"#1565C0",
  "藏青":"#1A237E","灰色":"#616161","卡其色":"#A1887F","米色":"#D7CCC8",
  "翠绿":"#43A047","墨绿":"#1B5E20","玫红":"#D8336B","浅灰":"#9E9E9E",
};
const getColor = (c: string) => COLOR_MAP[c] || "#888";
const isDark = (c: string) => ["黑色","深蓝","藏青","墨绿","紫色","灰色"].includes(c);

const PRESET_EVENTS = [
  { label:"结婚",icon:"💒"},{label:"搬家",icon:"📦"},{label:"开业",icon:"🎉"},
  { label:"出行",icon:"✈️"},{label:"动土",icon:"🏗️"},{label:"签约",icon:"📝"},
  { label:"入学",icon:"📚"},{label:"祭祀",icon:"🙏"},
];

export default function YijiPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showPersonal, setShowPersonal] = useState(false);
  const [uf, setUf] = useState<YijiParams>({ year:1990,month:5,day:20,hour:12,minute:0,gender:"男" });
  const [zejiAct, setZejiAct] = useState("");
  const [zejiRes, setZejiRes] = useState<any[]>([]);
  const [zejiLoad, setZejiLoad] = useState(false);
  const [expand, setExpand] = useState<Record<string,boolean>>({});

  const toggle = (k: string) => setExpand({...expand,[k]:!expand[k]});

  const fetchYiji = async (p?: YijiParams) => {
    setLoading(true);
    try { setData(await getYiji(p)); } catch(e){}
    setLoading(false);
  };

  useEffect(()=>{fetchYiji()},[]);
  // 每5分钟自动刷新
  useEffect(()=>{const t=setInterval(()=>fetchYiji(showPersonal?uf:undefined),300000);return ()=>clearInterval(t)},[showPersonal,uf]);

  const doZeji = async (a: string) => {
    setZejiAct(a); setZejiLoad(true);
    try { const r = await searchZeji(a,60); setZejiRes(r.dates||[]); }
    catch(e){} setZejiLoad(false);
  };

  if (loading&&!data) return (
    <div className="flex flex-col min-h-dvh pb-20 items-center justify-center">
      <Loader2 size={32} className="animate-spin text-gold"/>
      <p className="text-text-secondary text-sm mt-3">加载黄历...</p>
      <BottomNav/>
    </div>
  );

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* === 顶部总览（紧凑） === */}
      <div className="px-5 pt-6 pb-2">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-text-tertiary text-xs">{data?.lunar_date} · {data?.week}</p>
            <div className="flex items-baseline gap-3 mt-1">
              <span className="text-3xl font-[family-name:var(--font-display)] text-text">{data?.day_ganzhi}</span>
              <span className={`text-sm font-bold ${data?.tianshen_luck==="吉"?"text-green":"text-accent"}`}>
                {data?.tianshen}日
              </span>
            </div>
            <div className="flex gap-4 text-xs text-text-tertiary mt-1">
              <span>冲{data?.chong_shengxiao}</span>
              <span>煞{data?.sha_direction}</span>
              <span>{data?.jianchu}·{data?.xiu}</span>
              <button onClick={()=>fetchYiji(showPersonal?uf:undefined)}
                className="text-accent tap-active"><RefreshCw size={11}/></button>
            </div>
            {data?.fetched_at && (
              <p className="text-[9px] text-text-tertiary mt-1">更新于 {data.fetched_at}</p>
            )}
          </div>
          {/* 彭祖小提示 */}
          <div className="text-right text-[10px] text-text-tertiary leading-relaxed">
            <p>{data?.pengzu_gan}</p>
            <p>{data?.pengzu_zhi}</p>
          </div>
        </div>
      </div>

      <div className="px-5 flex-1 space-y-3">
        {/* === 宜忌（两列紧凑） === */}
        <div className="grid grid-cols-2 gap-3">
          <div className="dao-card py-3">
            <h3 className="text-xs font-bold text-green mb-2 flex items-center gap-1"><Star size={12}/>宜</h3>
            <div className="flex flex-wrap gap-1">
              {(data?.yi||[]).map((s:string)=><span key={s} className="px-2 py-0.5 bg-green/5 text-green text-[11px] rounded-full">{s}</span>)}
            </div>
          </div>
          <div className="dao-card py-3">
            <h3 className="text-xs font-bold text-accent mb-2 flex items-center gap-1"><AlertTriangle size={12}/>忌</h3>
            <div className="flex flex-wrap gap-1">
              {(data?.ji||[]).map((s:string)=><span key={s} className="px-2 py-0.5 bg-accent/5 text-accent text-[11px] rounded-full">{s}</span>)}
            </div>
          </div>
        </div>

        {/* === 个人开运（输入生日后显示） === */}
        {!showPersonal ? (
          <div className="dao-card py-3">
            <p className="text-xs text-text mb-2">输入生日，查看专属开运指南</p>
            <div className="flex gap-1.5 flex-wrap">
              <input type="number" value={uf.year} onChange={e=>setUf({...uf,year:+e.target.value})}
                className="w-14 bg-bg-subtle border border-border rounded-lg px-2 py-1.5 text-xs text-text" placeholder="年"/>
              <input type="number" value={uf.month} onChange={e=>setUf({...uf,month:+e.target.value})}
                className="w-10 bg-bg-subtle border border-border rounded-lg px-2 py-1.5 text-xs text-text" placeholder="月"/>
              <input type="number" value={uf.day} onChange={e=>setUf({...uf,day:+e.target.value})}
                className="w-10 bg-bg-subtle border border-border rounded-lg px-2 py-1.5 text-xs text-text" placeholder="日"/>
              <select value={uf.gender} onChange={e=>setUf({...uf,gender:e.target.value})}
                className="bg-bg-subtle border border-border rounded-lg px-2 py-1.5 text-xs text-text">
                <option>男</option><option>女</option>
              </select>
              <button onClick={()=>{setShowPersonal(true);fetchYiji(uf);}}
                className="bg-accent text-white px-3 py-1.5 rounded-lg text-xs tap-active ml-auto">查看</button>
            </div>
          </div>
        ) : (
          <>
            {/* 个人分析 */}
            {data?.personal?.analysis?.length>0 && (
              <div className="dao-card py-3 border-gold/30">
                <p className="text-xs text-text leading-relaxed">
                  {(data.personal.analysis||[]).map((a:string,i:number)=><span key={i}>{a} </span>)}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  {(data.personal.yi||[]).map((s:string)=><span key={s} className="px-1.5 py-0.5 bg-green/10 text-green text-[10px] rounded-full">{s}</span>)}
                  {(data.personal.ji||[]).map((s:string)=><span key={s} className="px-1.5 py-0.5 bg-accent/10 text-accent text-[10px] rounded-full">{s}</span>)}
                  <span className="ml-auto text-[10px] font-bold text-text-secondary">{data.personal.summary}</span>
                </div>
              </div>
            )}
            {/* 开运穿搭 */}
            {data?.daily_tips && (
              <div className="dao-card py-3 border-gold/30">
                <p className="text-xs font-bold text-text mb-2">今日开运</p>
                <div className="flex flex-wrap gap-1 mb-2">
                  {(data.daily_tips.wear_colors||[]).map((c:string)=>(
                    <span key={c} className="px-2 py-1 rounded-full text-[10px] font-medium text-white"
                      style={{backgroundColor:getColor(c)}}>{c}</span>
                  ))}
                </div>
                <p className="text-[11px] text-text leading-relaxed">{data.daily_tips.wear_detail}</p>
                <div className="grid grid-cols-2 gap-3 mt-2 text-[11px]">
                  <div><span className="text-green">宜：</span>{(data.daily_tips.suggest_do||[]).slice(0,3).join("、")}</div>
                  <div><span className="text-accent">忌：</span>{(data.daily_tips.suggest_avoid||[]).slice(0,3).join("、")}</div>
                </div>
                <p className="text-center text-xs text-gold italic mt-3">「{data.daily_tips.daily_quote}」</p>
              </div>
            )}
          </>
        )}

        {/* === 可折叠区域 === */}

        {/* 吉神方位 */}
        <button onClick={()=>toggle("dir")} className="w-full dao-card py-3 flex items-center justify-between">
          <span className="text-xs font-bold text-text">吉神方位</span>
          <span className="text-text-secondary flex items-center gap-2 text-[11px]">
            财{data?.caishen} 喜{data?.xishen} 福{data?.fushen}
            {expand.dir?<ChevronUp size={14}/>:<ChevronDown size={14}/>}
          </span>
        </button>
        {expand.dir && (
          <div className="dao-card py-3 space-y-2 anim-enter">
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              {[{l:"财神",v:data?.caishen},{l:"喜神",v:data?.xishen},{l:"福神",v:data?.fushen},
                {l:"阳贵",v:data?.yanggui},{l:"阴贵",v:data?.yingui},{l:"胎神",v:data?.taishen}].map(({l,v})=>(
                <div key={l} className="bg-bg-subtle rounded-lg py-2">
                  <p className="text-[10px] text-text-tertiary">{l}</p>
                  <p className="font-medium text-text">{v}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 择吉搜索 */}
        <button onClick={()=>toggle("zeji")} className="w-full dao-card py-3 flex items-center justify-between">
          <span className="text-xs font-bold text-text">择吉搜索</span>
          <span className="text-[11px] text-text-secondary">结婚·搬家·开业{expand.zeji?<ChevronUp size={14}/>:<ChevronDown size={14}/>}</span>
        </button>
        {expand.zeji && (
          <div className="dao-card py-3 space-y-3 anim-enter">
            <div className="grid grid-cols-4 gap-1.5">
              {PRESET_EVENTS.map(({label,icon})=>(
                <button key={label} onClick={()=>doZeji(label)}
                  className={`py-2 rounded-lg text-xs tap-active ${zejiAct===label?"bg-accent text-white":"bg-bg-subtle text-text"}`}>
                  <span className="block text-sm">{icon}</span>{label}
                </button>
              ))}
            </div>
            {zejiLoad && <Loader2 size={16} className="animate-spin text-gold mx-auto"/>}
            {zejiRes.length>0 && !zejiLoad && (
              <div className="space-y-1 max-h-[160px] overflow-y-auto">
                <p className="text-[10px] text-text-secondary">未来60天「{zejiAct}」· {zejiRes.length}天</p>
                {zejiRes.slice(0,6).map((d:any,i:number)=>(
                  <div key={i} className="flex justify-between text-[11px] py-1 px-2 bg-bg-subtle/50 rounded">
                    <span className="text-text">{d.date.slice(5)} {d.week}</span>
                    <span className="text-text-tertiary">{d.day_ganzhi} {d.jianchu}日 {d.tianshen}({d.tianshen_luck})</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 时辰吉凶 */}
        <button onClick={()=>toggle("hours")} className="w-full dao-card py-3 flex items-center justify-between">
          <span className="text-xs font-bold text-text">时辰吉凶</span>
          <span className="text-text-secondary">{expand.hours?<ChevronUp size={14}/>:<ChevronDown size={14}/>}</span>
        </button>
        {expand.hours && (
          <div className="dao-card py-3 anim-enter">
            <div className="grid grid-cols-4 gap-1">
              {(data?.hours||[]).slice(0,12).map((h:any)=>(
                <div key={h.name} className={`text-center rounded-lg py-1.5 ${
                  h.tianshen_luck==="吉"?"bg-green/5 border border-green/20":"bg-accent/3 border border-accent/10"}`}>
                  <p className="text-[10px] font-bold text-text">{h.name}</p>
                  <p className="text-[9px] text-text-tertiary">{h.ganzhi}</p>
                  <p className={`text-[9px] ${h.tianshen_luck==="吉"?"text-green":"text-accent"}`}>
                    {h.tianshen}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="text-center text-[10px] text-text-tertiary pb-2">
          本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义
        </p>
      </div>

      <BottomNav/>
    </div>
  );
}
