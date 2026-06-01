import type { Metadata, Viewport } from "next";
import { ZCOOL_XiaoWei, Ma_Shan_Zheng } from "next/font/google";
import "./globals.css";

const zcool = ZCOOL_XiaoWei({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dao-display",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
  themeColor: "#1C1814",
};

export const metadata: Metadata = {
  title: "命理溯源",
  description: "道藏秘卷 · 八字溯源 · 古籍考据 · 择吉黄历",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "命理溯源",
  },
  formatDetection: { telephone: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${zcool.variable} h-full`}>
      <body className="min-h-dvh flex flex-col max-w-[430px] mx-auto
                        bg-dao-paper text-dao-ink font-[family-name:var(--font-body)]
                        overflow-x-hidden relative">
        {/* 背景纹饰 */}
        <div className="dao-bg-pattern" />

        {/* 顶部八卦装饰 */}
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-[430px] h-1
                       bg-gradient-to-r from-transparent via-dao-gold/30 to-transparent z-50" />

        {children}
      </body>
    </html>
  );
}
