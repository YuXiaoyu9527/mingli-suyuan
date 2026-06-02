"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import DailyWisdom from "@/components/DailyWisdom";
import { getYiji, searchZeji, YijiParams } from "@/lib/api";
import { Loader2, RefreshCw, Compass, Star, AlertTriangle, Clock, Search } from "lucide-react";

export default function YijiPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showPersonal, setShowPersonal] = useState(false);
  const [userForm, setUserForm] = useState<YijiParams>({
    year: 1990, month: 5, day: 20, hour: 12, minute: 0, gender: "男",
  });

  const [zejiActivity, setZejiActivity] = useState("");
  const [zejiResults, setZejiResults] = useState<any[]>([]);
  const [zejiLoading, setZejiLoading] = useState(false);

  const PRESET_EVENTS = [
    { label: "结婚", icon: "💒" },
    { label: "搬家", icon: "📦" },
    { label: "开业", icon: "🎉" },
    { label: "出行", icon: "✈️" },
    { label: "动土", icon: "🏗️" },
    { label: "签约", icon: "📝" },
    { label: "入学", icon: "📚" },
    { label: "祭祀", icon: "🙏" },
  ];

  const fetchYiji = async (params?: YijiParams) => {
    setLoading(true);
    try {
      const result = await getYiji(params);
      setData(result);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const handleZejiSearch = async (activity: string) => {
    setZejiActivity(activity);
    setZejiLoading(true);
    try {
      const result = await searchZeji(activity, 60);
      setZejiResults(result.dates || []);
    } catch (e) { console.error(e); }
    setZejiLoading(false);
  };

  useEffect(() => { fetchYiji(); }, []);

  const handlePersonal = () => {
    fetchYiji(userForm);
    setShowPersonal(true);
  };

  if (loading && !data) {
    return (
      <div className="flex flex-col min-h-dvh pb-20 items-center justify-center">
        <Loader2 size={32} className="animate-spin text-gold" />
        <p className="text-aged text-sm mt-3">加载今日黄历...</p>
        <BottomNav />
      </div>
    );
  }

  const isJi = data?.tianshen_luck === "吉";
  const isHuangdao = data?.tianshen_type === "黄道";

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* === 顶部：干支主卡片 === */}
      <header className="px-5 pt-6 pb-3 text-center">
        <p className="text-xs text-aged-light">{data?.lunar_date} · {data?.week}</p>
        <div className="inline-flex items-center justify-center w-20 h-20
                       rounded-full border-2 border-vermillion my-3">
          <span className="text-3xl font-[family-name:var(--font-display)] text-vermillion">
            {data?.day_ganzhi}
          </span>
        </div>
        <div className="flex items-center justify-center gap-3 text-sm">
          <span className={isJi ? "text-auspicious font-bold" : "text-inauspicious font-bold"}>
            {data?.tianshen}({data?.tianshen_type}/{data?.tianshen_luck})
          </span>
          <span className="text-aged">·</span>
          <span className="text-aged">{data?.jianchu}日</span>
        </div>
        <div className="flex justify-center gap-4 mt-2 text-xs text-aged-light">
          <span>冲{data?.chong_shengxiao}</span>
          <span>煞{data?.sha_direction}</span>
          <span>{data?.xiu}星({data?.xiu_luck})</span>
        </div>
        <button onClick={() => fetchYiji(showPersonal ? userForm : undefined)}
          className="mt-2 text-xs text-indigo-traditional tap-active inline-flex items-center gap-1">
          <RefreshCw size={11} /> 刷新
        </button>
      </header>

      <div className="px-4 flex-1 space-y-4">
        {/* === 宜忌卡片 === */}
        <div className="grid grid-cols-2 gap-3">
          <div className="dao-card">
            <h3 className="text-sm font-bold text-auspicious mb-2 flex items-center gap-1">
              <Star size={14} /> 宜
            </h3>
            <div className="flex flex-wrap gap-1">
              {(data?.yi || []).map((item: string) => (
                <span key={item} className="px-2 py-0.5 bg-auspicious/10 text-auspicious text-xs
                                           rounded-full border border-auspicious/20">{item}</span>
              ))}
            </div>
          </div>
          <div className="dao-card">
            <h3 className="text-sm font-bold text-inauspicious mb-2 flex items-center gap-1">
              <AlertTriangle size={14} /> 忌
            </h3>
            <div className="flex flex-wrap gap-1">
              {(data?.ji || []).map((item: string) => (
                <span key={item} className="px-2 py-0.5 bg-inauspicious/10 text-inauspicious text-xs
                                           rounded-full border border-inauspicious/20">{item}</span>
              ))}
            </div>
          </div>
        </div>

        {/* === 吉神方位 === */}
        <div className="dao-card">
          <h3 className="text-xs text-aged mb-2 flex items-center gap-1">
            <Compass size={13} /> 吉神方位
          </h3>
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            {[
              { label: "财神", value: data?.caishen, color: "text-gold" },
              { label: "喜神", value: data?.xishen, color: "text-auspicious" },
              { label: "福神", value: data?.fushen, color: "text-indigo-traditional" },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-parchment-dark rounded-lg py-2">
                <p className="text-[10px] text-aged-light">{label}</p>
                <p className={`font-bold ${color}`}>{value}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-3 gap-2 text-center text-xs mt-2">
            {[
              { label: "阳贵", value: data?.yanggui },
              { label: "阴贵", value: data?.yingui },
              { label: "胎神", value: data?.taishen },
            ].map(({ label, value }) => (
              <div key={label} className="bg-parchment-dark rounded-lg py-2">
                <p className="text-[10px] text-aged-light">{label}</p>
                <p className="text-[10px] text-ink-light leading-tight">{value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* === 吉神凶煞 === */}
        <div className="dao-card">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p className="text-auspicious font-bold mb-1 text-[11px]">吉神</p>
              <div className="flex flex-wrap gap-1">
                {(data?.jishen || []).map((s: string) => (
                  <span key={s} className="text-[10px] text-auspicious">{s}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-inauspicious font-bold mb-1 text-[11px]">凶煞</p>
              <div className="flex flex-wrap gap-1">
                {(data?.xiongsha || []).map((s: string) => (
                  <span key={s} className="text-[10px] text-inauspicious">{s}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* === 时辰吉凶（折叠） === */}
        <details className="dao-card">
          <summary className="text-xs text-aged cursor-pointer flex items-center gap-1">
            <Clock size={13} /> 时辰吉凶（展开查看）
          </summary>
          <div className="mt-3 grid grid-cols-4 gap-1.5">
            {data?.hours?.slice(0, 12).map((h: any) => (
              <div key={h.name}
                className={`text-center rounded-lg py-1.5 px-1
                  ${h.tianshen_luck === "吉"
                    ? "bg-auspicious/5 border border-auspicious/20"
                    : "bg-inauspicious/5 border border-inauspicious/10"}`}>
                <p className="text-[10px] font-bold text-ink">{h.name}</p>
                <p className="text-[10px] text-aged-light">{h.ganzhi}</p>
                <p className={`text-[10px] ${h.tianshen_luck === "吉" ? "text-auspicious" : "text-inauspicious"}`}>
                  {h.tianshen}({h.tianshen_luck})
                </p>
              </div>
            ))}
          </div>
        </details>

        {/* === 个人宜忌 === */}
        {!showPersonal ? (
          <div className="dao-card">
            <p className="text-sm text-ink mb-3">想知道今日对你个人的影响？</p>
            <div className="flex gap-1.5 flex-wrap">
              <input type="number" value={userForm.year} onChange={e => setUserForm({...userForm, year: +e.target.value})}
                className="w-14 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="年"/>
              <input type="number" value={userForm.month} onChange={e => setUserForm({...userForm, month: +e.target.value})}
                className="w-10 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="月"/>
              <input type="number" value={userForm.day} onChange={e => setUserForm({...userForm, day: +e.target.value})}
                className="w-10 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="日"/>
              <select value={userForm.gender} onChange={e => setUserForm({...userForm, gender: e.target.value})}
                className="bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs">
                <option>男</option><option>女</option>
              </select>
              <button onClick={handlePersonal}
                className="bg-vermillion text-white px-3 py-1.5 rounded-lg text-xs tap-active">
                查看个人
              </button>
            </div>
          </div>
        ) : (
          data?.personal?.analysis?.length > 0 && (
            <div className="dao-card border-gold/30">
              <h3 className="text-sm font-bold text-ink mb-2">个人分析</h3>
              {(data.personal.analysis || []).map((a: string, i: number) => (
                <p key={i} className="text-xs text-ink-light leading-relaxed mb-1.5">{a}</p>
              ))}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-parchment-darker">
                <div className="flex gap-2">
                  {(data.personal.yi || []).map((item: string) => (
                    <span key={item} className="px-2 py-0.5 bg-auspicious/10 text-auspicious text-[11px] rounded-full">{item}</span>
                  ))}
                  {(data.personal.ji || []).map((item: string) => (
                    <span key={item} className="px-2 py-0.5 bg-inauspicious/10 text-inauspicious text-[11px] rounded-full">{item}</span>
                  ))}
                </div>
                <span className={`text-xs font-bold ${(data.personal.score||0) >= 0 ? "text-auspicious" : "text-inauspicious"}`}>
                  {data.personal.summary}
                </span>
              </div>
            </div>
          )
        )}

        {/* === 择吉搜索 === */}
        <div className="dao-card">
          <h3 className="text-xs text-dao-aged mb-3 flex items-center gap-1">
            <Search size={13} /> 择吉搜索 · 未来吉日
          </h3>
          <div className="grid grid-cols-4 gap-2 mb-3">
            {PRESET_EVENTS.map(({ label, icon }) => (
              <button key={label}
                onClick={() => handleZejiSearch(label)}
                className={`py-2.5 rounded-lg text-xs font-medium tap-active transition-colors
                  ${zejiActivity === label
                    ? "bg-dao-red text-white"
                    : "bg-dao-paper-dark text-dao-ink-light border border-dao-paper-darker hover:border-dao-gold/30"}`}>
                <span className="block text-base mb-0.5">{icon}</span>
                {label}
              </button>
            ))}
          </div>

          {zejiLoading && (
            <div className="text-center py-4">
              <Loader2 size={20} className="animate-spin text-dao-gold mx-auto" />
              <p className="text-xs text-dao-aged mt-1">搜索未来{zejiActivity}吉日...</p>
            </div>
          )}

          {!zejiLoading && zejiResults.length > 0 && (
            <div>
              <p className="text-[10px] text-dao-aged mb-2">
                未来60天适合「{zejiActivity}」· 共{zejiResults.length}天
              </p>
              <div className="space-y-1 max-h-[200px] overflow-y-auto">
                {zejiResults.slice(0, 8).map((d: any, i: number) => (
                  <div key={i} className="flex items-center justify-between py-1.5 px-2 rounded bg-dao-paper-dark/50 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="text-dao-ink font-medium">{d.date.slice(5)}</span>
                      <span className="text-dao-aged">{d.week}</span>
                      <span className="text-dao-aged-light">农历{d.lunar}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-dao-ink-light">{d.day_ganzhi} {d.jianchu}日</span>
                      <span className={d.tianshen_type === "黄道" ? "text-dao-jade text-[10px]" : "text-dao-aged text-[10px]"}>
                        {d.tianshen}({d.tianshen_luck})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* === 古籍出处 === */}
        <div className="classical-quote text-xs">
          <p className="text-[10px] text-aged-light mb-1">数据来源</p>
          {data?.classical_ref || "《协纪辨方书》·乾隆钦定 · 四库全书本"}
        </div>

        {/* 潮汐式日签 */}
        <DailyWisdom />

        <p className="text-center text-[11px] text-aged-light pb-4">
          本软件为易经学术工具，内容仅供传统文化研究与民俗参考，不等于专业测评，不代表任何价值评判，无任何现实指导意义
        </p>
      </div>

      <BottomNav />
    </div>
  );
}
