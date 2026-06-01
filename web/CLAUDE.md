# 前端子项目规则

本目录为 Next.js 16 + Tailwind CSS v4 前端。

## 技术要点
- Next.js 16 App Router（`app/` 目录）
- Tailwind CSS v4（使用 `@import "tailwindcss"` 和 `@theme inline`）
- `params` 和 `searchParams` 是 Promise，必须 await
- 字体使用 `next/font/google` 加载
- 移动端优先设计（基准宽度 375px，最大宽度 430px）

## 关键依赖版本
- next: 16.2.6
- react: 19.2.4
- tailwindcss: ^4

详见父目录 `../CLAUDE.md` 中的 AI 使用红线。
