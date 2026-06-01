"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { getYiji, YijiParams } from "@/lib/api";
import { ScrollText, Sparkles, AlertTriangle, Loader2, RefreshCw } from "lucide-react";

export default function YijiPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showPersonal, setShowPersonal] = useState(false);
  const [userForm, setUserForm] = useState<YijiParams>({
    year: 1990, month: 5, day: 20, hour: 12, minute: 0, gender: "男",
  });

  const fetchYiji = async (params?: YijiParams) => {
    setLoading(true);
    try {
      const result = await getYiji(params);
      setData(result);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchYiji();
  }, []);

  const handlePersonal = () => {
    fetchYiji(userForm);
    setShowPersonal(true);
  };

  if (loading && !data) {
    return (
      <div className="flex flex-col min-h-dvh pb-20 items-center justify-center">
        <Loader2 size={32} className="animate-spin text-gold" />
        <p className="text-aged text-sm mt-3">加载今日宜忌...</p>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          今日宜忌
        </h1>
        <p className="text-aged text-sm mt-1">
          建除十二神 · 黄道黑道 · 彭祖百忌
        </p>
      </header>

      <div className="px-5 flex-1 space-y-5">
        {/* 干支日期 */}
        <div className="text-center py-8 card-ancient">
          <div className="inline-flex items-center justify-center w-24 h-24
                         rounded-full border-2 border-vermillion mb-4">
            <span className="text-3xl font-[family-name:var(--font-display)] text-vermillion">
              {data?.day_ganzhi}
            </span>
          </div>
          <p className="text-aged text-sm">
            建除：<span className="text-ink font-bold">{data?.jianchu}日</span>
            {" · "}
            黄道：<span className={data?.huangdao_type === "黄道" ? "text-auspicious font-bold" : "text-inauspicious font-bold"}>
              {data?.huangdao_shen}({data?.huangdao_type})
            </span>
          </p>
          <p className="text-xs text-aged-light mt-1">{data?.jianchu_desc}</p>
          <p className="text-[11px] text-aged-light mt-2">
            {data?.pengzu_ji?.join(" · ")}
          </p>
          <button onClick={() => fetchYiji()} className="mt-3 text-xs text-indigo-traditional tap-active inline-flex items-center gap-1">
            <RefreshCw size={12} /> 刷新
          </button>
        </div>

        {/* 通用宜忌 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="card-ancient">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-auspicious" />
              <h3 className="text-sm font-bold text-ink">宜</h3>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(data?.general_yi || []).map((item: string) => (
                <span key={item} className="px-2.5 py-1 bg-auspicious/10 text-auspicious text-xs rounded-full border border-auspicious/20">
                  {item}
                </span>
              ))}
              {(!data?.general_yi?.length) && <span className="text-xs text-aged-light">—</span>}
            </div>
          </div>

          <div className="card-ancient">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={16} className="text-inauspicious" />
              <h3 className="text-sm font-bold text-ink">忌</h3>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(data?.general_ji || []).map((item: string) => (
                <span key={item} className="px-2.5 py-1 bg-inauspicious/10 text-inauspicious text-xs rounded-full border border-inauspicious/20">
                  {item}
                </span>
              ))}
              {(!data?.general_ji?.length) && <span className="text-xs text-aged-light">—</span>}
            </div>
          </div>
        </div>

        {/* 个人宜忌 */}
        {!showPersonal ? (
          <div className="card-ancient">
            <p className="text-sm text-ink mb-3">想知道今日对你个人的影响？</p>
            <div className="flex gap-2 flex-wrap">
              <input type="number" value={userForm.year} onChange={e => setUserForm({...userForm, year: +e.target.value})}
                className="w-16 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="1990"/>
              <span className="text-xs text-aged self-center">年</span>
              <input type="number" value={userForm.month} onChange={e => setUserForm({...userForm, month: +e.target.value})}
                className="w-12 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="5"/>
              <span className="text-xs text-aged self-center">月</span>
              <input type="number" value={userForm.day} onChange={e => setUserForm({...userForm, day: +e.target.value})}
                className="w-12 bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs" placeholder="20"/>
              <span className="text-xs text-aged self-center">日</span>
              <select value={userForm.gender} onChange={e => setUserForm({...userForm, gender: e.target.value})}
                className="bg-parchment-dark border border-parchment-darker rounded-lg px-2 py-1.5 text-ink text-xs">
                <option>男</option><option>女</option>
              </select>
              <button onClick={handlePersonal}
                className="bg-vermillion text-white px-3 py-1.5 rounded-lg text-xs tap-active ml-auto">
                查看个人宜忌
              </button>
            </div>
          </div>
        ) : (
          <>
            {data?.personal_analysis && (
              <div className="card-ancient">
                <h3 className="text-sm font-bold text-ink mb-2">个人分析</h3>
                <p className="text-sm text-ink-light leading-relaxed">{data.personal_analysis}</p>
              </div>
            )}
            {(data?.personal_yi?.length > 0 || data?.personal_ji?.length > 0) && (
              <div className="grid grid-cols-2 gap-3">
                <div className="card-ancient">
                  <h3 className="text-sm font-bold text-auspicious mb-2">个人宜</h3>
                  {(data?.personal_yi || []).map((item: string) => (
                    <span key={item} className="inline-block px-2 py-1 bg-auspicious/10 text-auspicious text-xs rounded-full border border-auspicious/20 mr-1 mb-1">
                      {item}
                    </span>
                  ))}
                </div>
                <div className="card-ancient">
                  <h3 className="text-sm font-bold text-inauspicious mb-2">个人忌</h3>
                  {(data?.personal_ji || []).map((item: string) => (
                    <span key={item} className="inline-block px-2 py-1 bg-inauspicious/10 text-inauspicious text-xs rounded-full border border-inauspicious/20 mr-1 mb-1">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* 古籍出处 */}
        <div className="classical-quote text-sm">
          《协纪辨方书·卷三》：建除十二神者，正月建寅，二月建卯，顺行十二辰，每月各有所建。凡建日，兵福所集，宜封拜、出行、修造……黄道者，天德、月德之所在，宜兴造、嫁娶、会友。黑道者，白虎、天刑之位，诸事不宜。
        </div>

        {/* 免责声明 */}
        <p className="text-center text-[11px] text-aged-light pb-4">
          仅供传统文化研究与民俗参考，不构成人生决策依据
        </p>
      </div>

      <BottomNav />
    </div>
  );
}
