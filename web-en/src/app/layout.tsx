import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0F0D15",
};

export const metadata: Metadata = {
  title: "DestinyScroll — Discover Your Element",
  description: "Ancient Chinese wisdom meets modern self-discovery. Discover your BaZi element blueprint.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-dvh max-w-[480px] mx-auto antialiased">
        {children}
      </body>
    </html>
  );
}
