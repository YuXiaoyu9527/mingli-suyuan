"use client";

/**
 * PWA 安装提示
 * ============
 * 当浏览器支持 PWA 安装且用户尚未安装时，在底部显示一个轻量横幅。
 * 点击后触发浏览器原生安装流程（添加到桌面）。
 *
 * 触发条件：
 * 1. 浏览器支持 beforeinstallprompt 事件
 * 2. 用户未通过其他方式关闭过提示
 * 3. 应用尚未被安装
 */

import { useState, useEffect } from "react";
import { Download, X } from "lucide-react";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export default function PWAInstallBanner() {
  const [deferredPrompt, setDeferredPrompt] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [showBanner, setShowBanner] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // 检查是否已经被安装
    if (window.matchMedia("(display-mode: standalone)").matches) {
      return;
    }

    // 检查是否之前关闭过
    const closed = localStorage.getItem("pwa-banner-closed");
    if (closed) {
      const closedTime = parseInt(closed);
      // 7天后重新提示
      if (Date.now() - closedTime < 7 * 24 * 60 * 60 * 1000) {
        return;
      }
    }

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowBanner(true);
    };

    window.addEventListener("beforeinstallprompt", handler);

    // 如果已安装
    window.addEventListener("appinstalled", () => {
      setShowBanner(false);
      setDeferredPrompt(null);
    });

    return () => {
      window.removeEventListener("beforeinstallprompt", handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;
    if (choice.outcome === "accepted") {
      setShowBanner(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowBanner(false);
    setDismissed(true);
    localStorage.setItem("pwa-banner-closed", Date.now().toString());
  };

  if (!showBanner && !dismissed) return null;
  if (!showBanner) return null;

  return (
    <div className="fixed bottom-16 left-1/2 -translate-x-1/2 w-[calc(100%-2rem)] max-w-[400px]
                    z-40 animate-slide-up">
      <div className="flex items-center gap-3 px-4 py-3
                      bg-[#1C1814] border border-gold/30 rounded-xl
                      shadow-lg shadow-black/30">
        {/* 图标 */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#C43A31] to-[#8B2020]
                        flex items-center justify-center flex-shrink-0">
          <span className="text-white text-lg">☯</span>
        </div>

        {/* 文案 */}
        <div className="flex-1 min-w-0">
          <p className="text-white text-xs font-medium truncate">
            添加到桌面
          </p>
          <p className="text-text-secondary text-[10px]">
            即开即用 · 离线也能查
          </p>
        </div>

        {/* 按钮 */}
        <button
          onClick={handleInstall}
          className="px-3 py-1.5 bg-gold text-white text-xs rounded-full
                     font-medium tap-active flex-shrink-0
                     hover:bg-amber-600 transition-colors"
        >
          <Download size={12} className="inline mr-1" />
          安装
        </button>

        {/* 关闭 */}
        <button
          onClick={handleDismiss}
          className="text-text-tertiary hover:text-text-secondary flex-shrink-0"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}