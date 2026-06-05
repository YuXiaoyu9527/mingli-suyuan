"use client";

/**
 * PWA 注册组件
 * ============
 * 在客户端注册 Service Worker 并渲染安装提示。
 * 必须在 layout.tsx 中作为 Client Component 引入。
 */

import { useEffect } from "react";
import PWAInstallBanner from "./PWAInstallBanner";

export default function PWARegister() {
  useEffect(() => {
    if (typeof window === "undefined" || !("serviceWorker" in navigator)) {
      return;
    }

    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("[PWA] Service Worker 已注册:", registration.scope);

        // 监听更新
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          if (!newWorker) return;
          newWorker.addEventListener("statechange", () => {
            if (
              newWorker.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              console.log("[PWA] 新版本已就绪，刷新后生效");
            }
          });
        });
      })
      .catch((err) => {
        console.warn("[PWA] Service Worker 注册失败:", err);
      });
  }, []);

  return <PWAInstallBanner />;
}