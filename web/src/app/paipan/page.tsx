"use client";

import BottomNav from "@/components/BottomNav";

export default function PaipanPage() {
  return (
    <div className="flex flex-col min-h-dvh pb-20">
      {/* 顶部 */}
      <header className="px-5 pt-10 pb-4">
        <h1 className="text-2xl text-vermillion font-[family-name:var(--font-display)] tracking-wider">
          八字排盘
        </h1>
        <p className="text-aged text-sm mt-1">
          公历日期 · 真太阳时 · 以立春换年
        </p>
      </header>

      {/* 排盘表单 */}
      <div className="px-5 flex-1 space-y-5">
        {/* 输入区域 */}
        <div className="card-ancient space-y-4">
          {/* 日期 */}
          <div>
            <label className="block text-xs text-aged mb-1.5 font-medium">
              公历日期
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="1990"
                className="flex-1 bg-parchment-dark border border-parchment-darker
                           rounded-lg px-3 py-2.5 text-ink text-sm
                           focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                           transition-all"
              />
              <span className="text-aged self-center">年</span>
              <input
                type="number"
                placeholder="05"
                min={1}
                max={12}
                className="w-16 bg-parchment-dark border border-parchment-darker
                           rounded-lg px-3 py-2.5 text-ink text-sm
                           focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                           transition-all"
              />
              <span className="text-aged self-center">月</span>
              <input
                type="number"
                placeholder="20"
                min={1}
                max={31}
                className="w-16 bg-parchment-dark border border-parchment-darker
                           rounded-lg px-3 py-2.5 text-ink text-sm
                           focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                           transition-all"
              />
              <span className="text-aged self-center">日</span>
            </div>
          </div>

          {/* 时间 */}
          <div>
            <label className="block text-xs text-aged mb-1.5 font-medium">
              出生时间
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="14"
                min={0}
                max={23}
                className="w-16 bg-parchment-dark border border-parchment-darker
                           rounded-lg px-3 py-2.5 text-ink text-sm
                           focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                           transition-all"
              />
              <span className="text-aged self-center">时</span>
              <input
                type="number"
                placeholder="30"
                min={0}
                max={59}
                className="w-16 bg-parchment-dark border border-parchment-darker
                           rounded-lg px-3 py-2.5 text-ink text-sm
                           focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                           transition-all"
              />
              <span className="text-aged self-center">分</span>
            </div>
          </div>

          {/* 地点 */}
          <div>
            <label className="block text-xs text-aged mb-1.5 font-medium">
              出生地点
            </label>
            <input
              type="text"
              placeholder="如：北京、上海、成都……"
              className="w-full bg-parchment-dark border border-parchment-darker
                         rounded-lg px-3 py-2.5 text-ink text-sm
                         focus:outline-none focus:border-vermillion focus:ring-1 focus:ring-vermillion/20
                         transition-all"
            />
            <p className="text-[11px] text-aged-light mt-1">
              用于真太阳时校正，输入城市名即可
            </p>
          </div>

          {/* 提交按钮 */}
          <button className="btn-primary w-full mt-4">
            开始排盘
          </button>
        </div>

        {/* 结果展示区（排盘后显示） */}
        <div className="card-ancient animate-fade-in-up">
          <div className="flex items-center gap-3 mb-4">
            <div className="seal-mark">经</div>
            <div>
              <p className="text-xs text-aged">排盘结果预览</p>
              <p className="text-sm text-ink font-medium">
                排盘功能即将接入 lunar-python 引擎
              </p>
            </div>
          </div>

          {/* 八字展示骨架 */}
          <div className="grid grid-cols-4 gap-3 text-center mt-4">
            {["年柱", "月柱", "日柱", "时柱"].map((label) => (
              <div key={label}>
                <p className="text-[11px] text-aged mb-1">{label}</p>
                <div className="bg-parchment-dark rounded-lg py-3">
                  <p className="text-lg font-[family-name:var(--font-display)] text-ink-light skeleton h-7 w-12 mx-auto rounded" />
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-aged-light text-center mt-4 italic">
            排盘引擎开发中，敬请期待
          </p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
