"use client";

/**
 * 八字分享卡组件
 * 灵感来源: 测测App 的测试结果分享图
 *
 * 生成一张可以截图分享的八字名片
 */

export default function ShareCard({
  ganzhi,
  rizhu,
  rizhuWuxing,
  nayin,
  lunarDate,
}: {
  ganzhi: string[];
  rizhu: string;
  rizhuWuxing: string;
  nayin: string;
  lunarDate: string;
}) {
  const handleShare = async () => {
    // Web Share API
    if (navigator.share) {
      try {
        await navigator.share({
          title: "我的八字命盘",
          text: `八字：${ganzhi.join(" ")}\n日主：${rizhu}(${rizhuWuxing})\n纳音：${nayin}\n农历：${lunarDate}\n—— 来自「命理溯源」`,
          url: window.location.href,
        });
      } catch {
        // 用户取消分享
      }
    } else {
      // 降级方案：复制到剪贴板
      const text = `八字：${ganzhi.join(" ")}\n日主：${rizhu}(${rizhuWuxing})\n纳音：${nayin}\n农历：${lunarDate}\n—— 来自「命理溯源」`;
      await navigator.clipboard.writeText(text);
      alert("已复制到剪贴板");
    }
  };

  return (
    <div className="relative">
      {/* 分享卡片视觉（截图用） */}
      <div className="dao-card text-center py-6 space-y-3" id="share-card">
        {/* 标题 */}
        <p className="text-[10px] text-text-secondary tracking-[0.2em]">道 藏 秘 卷</p>

        {/* 八字展示 */}
        <div className="flex justify-center gap-3">
          {["年", "月", "日", "时"].map((label, i) => (
            <div key={label}>
              <p className="text-[9px] text-text-secondary mb-1">{label}</p>
              <div className="pillar-block min-w-[48px] py-2">
                <p className="text-sm font-[family-name:var(--font-display)] text-text">
                  {ganzhi[i]?.[0]}
                </p>
                <p className="text-sm font-[family-name:var(--font-display)] text-accent">
                  {ganzhi[i]?.[1]}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* 日主 */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5
                       bg-accent/5 rounded-full border border-accent/20">
          <span className="text-xs text-text-secondary">日主</span>
          <span className="text-lg font-[family-name:var(--font-display)] text-accent">
            {rizhu}
          </span>
          <span className="text-xs text-text-tertiary">({rizhuWuxing})</span>
        </div>

        {/* 纳音 */}
        <p className="text-[11px] text-text-tertiary">纳音：{nayin}</p>
        <p className="text-[10px] text-text-tertiary">{lunarDate}</p>

        {/* 水印 */}
        <p className="text-[9px] text-gold/50 tracking-[0.3em]">
          命 理 溯 源
        </p>
      </div>

      {/* 分享按钮 */}
      <button
        onClick={handleShare}
        className="mt-4 w-full py-2.5 bg-bg-subtle border border-border
                   rounded-lg text-xs text-text tap-active flex items-center justify-center gap-1.5"
      >
        📤 分享我的八字
      </button>
    </div>
  );
}
