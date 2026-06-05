import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 🔧 低内存优化配置
  // 在笔记本(4-8GB RAM)上关闭以下选项可减少 ~200-300MB 内存占用

  // 生产构建时禁用 source map（省内存）
  productionBrowserSourceMaps: false,

  // 关闭实验性 Turbopack（它比 webpack 吃更多内存）
  // 如需极致省内存，手动启动: npm run dev -- --turbo=false

  // 限制构建并发
  experimental: {
    // 减少并行构建的页面数
    workerThreads: false,
  },
};

export default nextConfig;