"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { id: "mingli", label: "命理", icon: "☯", href: "/mingli" },
  { id: "yiji", label: "择吉", icon: "☲", href: "/yiji" },
  { id: "fengshui", label: "风水", icon: "☶", href: "/fengshui" },
  { id: "xuetang", label: "学堂", icon: "☰", href: "/xuetang" },
  { id: "dianji", label: "典籍", icon: "☷", href: "/dianji" },
];

export default function BottomNav() {
  const pathname = usePathname();
  const isActive = (id: string) => pathname.startsWith(`/${id}`) || (id === "xuetang" && pathname === "/");

  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px]
                    bg-dao-paper/97 backdrop-blur-xl safe-bottom z-50"
         style={{ borderTop: "1px solid var(--color-dao-paper-darker)" }}>
      <div className="flex items-center justify-around h-[64px] px-0.5">
        {tabs.map((tab) => {
          const active = isActive(tab.id);
          return (
            <Link key={tab.id} href={tab.href}
              className={`flex flex-col items-center justify-center gap-0.5
                         min-w-[56px] py-1 rounded-lg tap-active
                         transition-all duration-200 relative
                         ${active ? "text-dao-red" : "text-dao-aged hover:text-dao-ink-light"}`}>
              <span className={`text-lg transition-all duration-300
                ${active ? "scale-110 opacity-100" : "opacity-40"}`}>{tab.icon}</span>
              <span className={`text-[10px] tracking-widest transition-all duration-200
                ${active ? "font-bold" : "font-normal"}`}>{tab.label}</span>
              {active && <span className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-6 h-[2px] bg-dao-gold rounded-full"/>}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
