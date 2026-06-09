"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import BottomNav from "@/components/BottomNav";
import {
  User, Bookmark, BookOpen, Settings, Shield,
  MessageCircle, Plus, Trash2, ChevronRight,
} from "lucide-react";

interface BaziProfile {
  id: string;
  name: string;
  year: number;
  month: number;
  day: number;
  hour: number;
  gender: string;
  bazi?: string;
  createdAt: string;
}

/** 安全读写 localStorage — SSR 环境下返回 fallback 值 */
function safeGet<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try { return JSON.parse(localStorage.getItem(key) || "null") ?? fallback; }
  catch { return fallback; }
}
function safeSet(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  localStorage.setItem(key, JSON.stringify(value));
}

export default function MyPage() {
  const router = useRouter();
  const [profiles, setProfiles] = useState<BaziProfile[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [wrongCount, setWrongCount] = useState(0);
  const [newProfile, setNewProfile] = useState({
    name: "", year: 1990, month: 5, day: 20, hour: 12, gender: "男",
  });

  // 所有浏览器 API 调用全部收敛在 useEffect 中
  useEffect(() => {
    setProfiles(safeGet<BaziProfile[]>("bazi_profiles", []));
    setWrongCount(safeGet<unknown[]>("xuetang_wrong_book", []).length);
  }, []);

  const saveProfiles = (list: BaziProfile[]) => {
    setProfiles(list);
    safeSet("bazi_profiles", list);
  };

  const addProfile = () => {
    if (!newProfile.name.trim()) return;
    const profile: BaziProfile = {
      id: Date.now().toString(36),
      name: newProfile.name,
      year: newProfile.year,
      month: newProfile.month,
      day: newProfile.day,
      hour: newProfile.hour,
      gender: newProfile.gender,
      createdAt: new Date().toISOString(),
    };
    saveProfiles([profile, ...profiles]);
    setNewProfile({ name: "", year: 1990, month: 5, day: 20, hour: 12, gender: "男" });
    setShowAddForm(false);
  };

  const deleteProfile = (id: string) => {
    saveProfiles(profiles.filter((p) => p.id !== id));
  };

  const handleJumpPaipan = (p: BaziProfile) => {
    router.push(
      `/paipan?year=${p.year}&month=${p.month}&day=${p.day}&hour=${p.hour}&name=${encodeURIComponent(p.name)}`
    );
  };

  return (
    <div className="flex flex-col min-h-dvh pb-24">
      {/* 顶部个人信息 */}
      <header className="px-5 pt-8 pb-4 anim-page-enter">
        <div className="flex items-center gap-4">
          {/* 古风头像 */}
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#C43A31]/10 to-[#C9A96E]/20
                         border-2 border-gold/30 flex items-center justify-center flex-shrink-0">
            <User size={28} className="text-gold/70" />
          </div>
          <div>
            <h1 className="text-xl font-[family-name:var(--font-display)] text-text">
              溯源居士
            </h1>
            <p className="text-xs text-text-secondary mt-0.5">
              命理研习者 · 格物致知
            </p>
          </div>
        </div>
      </header>

      <div className="px-5 flex-1 space-y-4 anim-stagger-8">
        {/* ===== 亲友档案库 ===== */}
        <div className="dao-card">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-text flex items-center gap-2">
              <Bookmark size={16} className="text-accent" />
              亲友档案库
            </h3>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-1 text-[10px] text-gold tap-active"
            >
              <Plus size={14} />
              {showAddForm ? "收起" : "新增"}
            </button>
          </div>

          {/* 新增表单 */}
          {showAddForm && (
            <div className="bg-bg-subtle rounded-lg p-3 mb-3 space-y-2 anim-enter">
              <input
                type="text" value={newProfile.name}
                onChange={(e) => setNewProfile({ ...newProfile, name: e.target.value })}
                placeholder="姓名（如：曾国藩）"
                className="w-full bg-white border border-border rounded-lg px-3 py-2.5
                           text-text text-sm focus:outline-none focus:border-gold"
              />
              <div className="grid grid-cols-4 gap-2">
                {[
                  { k: "year", p: "年" },
                  { k: "month", p: "月" },
                  { k: "day", p: "日" },
                  { k: "hour", p: "时" },
                ].map(({ k, p }) => (
                  <div key={k} className="flex flex-col gap-0.5">
                    <label className="text-[9px] text-text-tertiary text-center">{p}</label>
                    <input
                      type="number"
                      value={(newProfile as any)[k]}
                      onChange={(e) =>
                        setNewProfile({ ...newProfile, [k]: +e.target.value })
                      }
                      className="w-full bg-white border border-border rounded-lg px-1 py-2.5
                                 text-text text-sm text-center focus:outline-none focus:border-gold"
                      placeholder={p}
                    />
                  </div>
                ))}
              </div>
              <div className="flex gap-2 items-center">
                <label className="text-[9px] text-text-tertiary">性别</label>
                <select
                  value={newProfile.gender}
                  onChange={(e) =>
                    setNewProfile({ ...newProfile, gender: e.target.value })
                  }
                  className="bg-white border border-border rounded-lg px-3 py-2.5
                             text-text text-sm focus:outline-none"
                >
                  <option>男</option>
                  <option>女</option>
                </select>
                <button
                  onClick={addProfile}
                  className="ml-auto bg-accent text-white px-4 py-2 rounded-lg text-xs tap-active"
                >
                  保存
                </button>
              </div>
            </div>
          )}

          {/* 档案列表 */}
          {profiles.length === 0 ? (
            <p className="text-xs text-text-tertiary text-center py-4">
              暂无档案 · 点击"新增"添加亲友八字
            </p>
          ) : (
            <div className="space-y-2 max-h-[40vh] overflow-y-auto no-scrollbar">
              {profiles.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center gap-3 p-3 bg-bg-subtle rounded-lg
                             tap-active hover:bg-bg-dark/50 transition-colors group"
                >
                  <button
                    onClick={() => handleJumpPaipan(p)}
                    className="flex-1 flex items-center gap-3 text-left"
                  >
                    <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                      <User size={16} className="text-accent/60" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text">{p.name}</p>
                      <p className="text-[10px] text-text-tertiary">
                        {p.year}.{p.month}.{p.day} · {p.gender} · {p.bazi || "待排盘"}
                      </p>
                    </div>
                    <ChevronRight size={14} className="text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                  <button
                    onClick={() => deleteProfile(p.id)}
                    className="text-text-tertiary hover:text-accent tap-active p-1"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ===== 学堂与研读沉淀 ===== */}
        <div className="dao-card">
          <h3 className="text-sm font-bold text-text flex items-center gap-2 mb-3">
            <BookOpen size={16} className="text-gold" />
            学堂与研读沉淀
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {/* 错题本 */}
            <button
              onClick={() => router.push("/xuetang?show=wrong")}
              className="bg-bg-subtle rounded-lg p-4 text-center tap-active hover:bg-bg-dark/50 transition-colors"
            >
              <div className="text-2xl mb-1">📝</div>
              <p className="text-xs font-medium text-text">我的错题本</p>
              <p className="text-[10px] text-text-tertiary mt-1">
                {wrongCount > 0 ? `${wrongCount} 道待复习` : "暂无错题"}
              </p>
            </button>
            {/* 收藏古籍 */}
            <button
              onClick={() => router.push("/dianji")}
              className="bg-bg-subtle rounded-lg p-4 text-center tap-active hover:bg-bg-dark/50 transition-colors"
            >
              <div className="text-2xl mb-1">📖</div>
              <p className="text-xs font-medium text-text">收藏的古籍</p>
              <p className="text-[10px] text-text-tertiary mt-1">
                浏览典籍
              </p>
            </button>
          </div>
        </div>

        {/* ===== 系统设置与咨询 ===== */}
        <div className="dao-card divide-y divide-border/50">
          <h3 className="text-sm font-bold text-text flex items-center gap-2 mb-3">
            <Settings size={16} className="text-text-secondary" />
            系统设置与咨询
          </h3>

          {/* 默认出生城市 */}
          <button className="w-full flex items-center justify-between py-3 text-left tap-active">
            <div className="flex items-center gap-3">
              <span className="text-lg">📍</span>
              <div>
                <p className="text-sm text-text">默认出生城市</p>
                <p className="text-[10px] text-text-tertiary">北京 (用于真太阳时校正)</p>
              </div>
            </div>
            <ChevronRight size={14} className="text-text-tertiary" />
          </button>

          {/* 免责声明 */}
          <button
            onClick={() => {
              alert(
                "本软件为易经学术工具，所有排盘结果由 lunar-python 引擎计算，" +
                "AI 解读基于 DeepSeek 模型生成。内容仅供传统文化研究与民俗参考，" +
                "不构成人生决策依据，不代表任何价值评判，无任何现实指导意义。"
              );
            }}
            className="w-full flex items-center justify-between py-3 text-left tap-active"
          >
            <div className="flex items-center gap-3">
              <Shield size={18} className="text-text-secondary" />
              <div>
                <p className="text-sm text-text">免责声明</p>
                <p className="text-[10px] text-text-tertiary">使用条款与学术声明</p>
              </div>
            </div>
            <ChevronRight size={14} className="text-text-tertiary" />
          </button>

          {/* 联系掌柜 */}
          <a
            href="mailto:yuxiaoyu9527@gmail.com?subject=命理溯源-高级咨询"
            className="flex items-center justify-between py-3 tap-active"
          >
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-gold/10 flex items-center justify-center">
                <MessageCircle size={14} className="text-gold" />
              </div>
              <div>
                <p className="text-sm text-gold font-medium">高级命理咨询</p>
                <p className="text-[10px] text-text-tertiary">联系掌柜 · 深度解读</p>
              </div>
            </div>
            <ChevronRight size={14} className="text-gold/60" />
          </a>
        </div>

        {/* 版本号 */}
        <p className="text-center text-[10px] text-text-tertiary py-4">
          命理溯源 v0.2.0 · 道藏秘卷
        </p>
      </div>

      <BottomNav />
    </div>
  );
}