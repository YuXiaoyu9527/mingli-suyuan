"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { id: "jinri", label: "今日", icon: "🏮", href: "/jinri" },
  { id: "paipan", label: "排盘", icon: "☯", href: "/paipan" },
  { id: "xuetang", label: "学堂", icon: "📚", href: "/xuetang" },
];

export default function BottomNav() {
  const pathname = usePathname();
  const isActive = (id: string) => pathname.startsWith(`/${id}`);

  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px]
                    bg-white/95 backdrop-blur-xl safe-bottom z-50 border-t border-border">
      <div className="flex items-center justify-around h-[56px]">
        {tabs.map((tab) => {
          const active = isActive(tab.id);
          return (
            <Link key={tab.id} href={tab.href}
              className={`flex flex-col items-center justify-center gap-0.5
                         min-w-[56px] py-1 rounded-lg tap-active transition-colors
                         ${active ? "text-accent" : "text-text-tertiary"}`}>
              <span className={`text-lg ${active ? "opacity-100" : "opacity-50"}`}>{tab.icon}</span>
              <span className={`text-[10px] ${active ? "font-semibold" : "font-normal"}`}>{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}