"use client";

import { useEffect, useState } from "react";

export default function LoadingSplash({ message = "推演中..." }: { message?: string }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center
                    bg-dao-paper anim-fade">
      {/* 八卦环绕 */}
      <div className="relative w-32 h-32 mb-8">
        {/* 太极图 */}
        <div className="taiji-loader absolute inset-0 m-auto" />

        {/* 八卦符号环绕 */}
        {["☰","☷","☳","☶","☵","☲","☴","☱"].map((sym, i) => {
          const angle = (i * 45 - 90) * Math.PI / 180;
          const r = 56;
          const x = Math.cos(angle) * r;
          const y = Math.sin(angle) * r;
          return (
            <span key={i}
              className="absolute text-dao-gold bagua-symbol"
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                transform: "translate(-50%, -50%)",
                fontSize: "1rem",
                opacity: 0.12,
                animation: `fadeIn 0.5s ${i * 0.1}s both`,
              }}>
              {sym}
            </span>
          );
        })}
      </div>

      {/* 标题 */}
      <h1 className="text-2xl font-[family-name:var(--font-display)] text-dao-red
                     tracking-[0.2em] mb-2 anim-enter">
        命 理 溯 源
      </h1>
      <p className="text-xs text-dao-aged tracking-[0.3em] anim-fade">
        {message}
      </p>
    </div>
  );
}
