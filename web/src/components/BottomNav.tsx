"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { id: "xuetang", label: "学堂", icon: "☰", href: "/xuetang" },
  { id: "paipan", label: "排盘", icon: "☯", href: "/paipan" },
  { id: "yiji", label: "黄历", icon: "☲", href: "/yiji" },
  { id: "mingli", label: "命例", icon: "☷", href: "/mingli" },
];

export default function BottomNav() {
  const pathname = usePathname();

  const isActive = (id: string) => {
    if (id === "paipan" && pathname === "/") return true;
    return pathname.startsWith(`/${id}`);
  };

  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px]
                    bg-dao-paper/97 backdrop-blur-xl safe-bottom z-50"
         style={{ borderTop: "1px solid var(--color-dao-paper-darker)" }}>
      <div className="flex items-center justify-around h-[64px] px-1">
        {tabs.map((tab) => {
          const active = isActive(tab.id);
          return (
            <Link
              key={tab.id}
              href={tab.href}
              className={`flex flex-col items-center justify-center gap-0.5
                         min-w-[60px] py-1 px-2 rounded-lg tap-active
                         transition-all duration-200 relative
                         ${active ? "text-dao-red" : "text-dao-aged hover:text-dao-ink-light"}`}
            >
              {/* 八卦符号 */}
              <span className={`text-xl transition-all duration-300
                ${active ? "scale-110 opacity-100" : "opacity-40"}`}>
                {tab.icon}
              </span>

              {/* 标签 */}
              <span className={`text-[11px] tracking-widest transition-all duration-200
                ${active ? "font-bold" : "font-normal"}`}>
                {tab.label}
              </span>

              {/* 选中指示（鎏金短线） */}
              {active && (
                <span className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-8 h-[2px]
                               bg-dao-gold rounded-full" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
