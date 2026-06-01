import type { Metadata, Viewport } from "next";
import { ZCOOL_XiaoWei } from "next/font/google";
import "./globals.css";

const zcoolXiaoWei = ZCOOL_XiaoWei({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-zcool-xiaowei",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
  themeColor: "#F5F0E8",
};

export const metadata: Metadata = {
  title: "命理溯源",
  description: "基于古籍考据的传统命理学习与择吉工具",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "命理溯源",
  },
  formatDetection: {
    telephone: false,
  },
  icons: {
    apple: "/icon-192.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${zcoolXiaoWei.variable} h-full`}
    >
      <body className="min-h-dvh flex flex-col max-w-[430px] mx-auto bg-parchment text-ink font-[family-name:var(--font-body)] overflow-x-hidden">
        {children}
      </body>
    </html>
  );
}
