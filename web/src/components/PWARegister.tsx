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
    // 暂时禁用 Service Worker 以避免缓存锁死新版本
    // 等部署稳定后再开启
    if (typeof window === "undefined" || !("serviceWorker" in navigator)) {
      return;
    }

    // 先注销所有旧 SW，确保浏览器拿到最新内容
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      registrations.forEach((reg) => reg.unregister());
      console.log("[PWA] 已清除旧 Service Worker");
    });
  }, []);

  return <PWAInstallBanner />;
}