"use client";

import { Compass, ScrollText, Swords, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  {
    id: "paipan",
    label: "排盘",
    icon: Compass,
    href: "/paipan",
    description: "八字排盘",
  },
  {
    id: "yiji",
    label: "宜忌",
    icon: ScrollText,
    href: "/yiji",
    description: "今日宜忌",
  },
  {
    id: "duanan",
    label: "断案",
    icon: Swords,
    href: "/duanan",
    description: "断案录",
  },
  {
    id: "mingli",
    label: "命例",
    icon: Users,
    href: "/mingli",
    description: "历史命例",
  },
];

export default function BottomNav() {
  const pathname = usePathname();

  // 高亮当前 tab：URL 路径包含 tab id
  const isActive = (id: string) => {
    if (id === "paipan" && pathname === "/") return true;
    return pathname.startsWith(`/${id}`);
  };

  return (
    <nav
      className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px]
                    bg-parchment/95 backdrop-blur-md border-t border-parchment-darker
                    safe-bottom z-50"
      style={{ boxShadow: "var(--shadow-nav)" }}
    >
      <div className="flex items-center justify-around h-16 px-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = isActive(tab.id);

          return (
            <Link
              key={tab.id}
              href={tab.href}
              className={`flex flex-col items-center justify-center gap-1
                         min-w-[64px] py-1 px-2 rounded-lg tap-active
                         transition-colors duration-150
                         ${active
                           ? "text-vermillion"
                           : "text-aged hover:text-ink-light"
                         }`}
            >
              <Icon
                size={22}
                strokeWidth={active ? 2.5 : 1.8}
                className="transition-all duration-150"
              />
              <span
                className={`text-xs font-medium transition-all duration-150
                           ${active ? "font-bold" : "font-normal"}`}
              >
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
