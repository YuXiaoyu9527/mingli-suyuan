# 命理溯源 · 项目记忆

> 🤖 本文件是项目的"外部大脑"。每次开发新功能前，Claude Code 应先读取此文件了解上下文。
> 每次重大改动后，更新此文件。格式：日期 + 事件 + 决策理由。

---

## 项目速览

| 项 | 值 |
|---|---|
| 项目名 | 命理溯源 (Mingli Suyuan) |
| 定位 | 古籍数字化 + RAG + 精准排盘 的命理学习考据工具 |
| 版本 | v0.2.0 → v0.3.0 推进中 |
| GitHub | `https://github.com/YuXiaoyu9527/mingli-suyuan` |
| 前端部署 | Netlify (base: `web/`) |
| 后端部署 | Railway (待上线) |
| 线上地址 | Netlify 自动分配的域名 |

---

## 技术栈速查

```
前端: Next.js 16 + React 19 + Tailwind CSS v4 + Framer Motion + TypeScript
后端: FastAPI + Python 3.13 (lunar-python 排盘引擎)
向量: ChromaDB / SimpleSearcher v2 (BGE-M3 嵌入)
AI:   DeepSeek-V4 (OpenAI 兼容 API)
部署: Netlify (前端) + Railway (后端)
```

---

## 项目结构要点

```
创业项目/
├── CLAUDE.md              # 项目宪法（AI 红线 + 开发规范 + 玄学 UI 规范）
├── PROJECT_MEMORY.md       # ← 本文件（项目记忆）
├── web/                   # Next.js 前端 (base dir for Netlify)
│   └── src/app/           # 页面路由
├── api/                   # FastAPI 后端
│   ├── server.py          # 统一 API 入口
│   ├── paipan/            # 排盘/格局/用神/神煞/起名/合婚/风水/择吉/周易
│   ├── ai/                # AI 解读器 (DeepSeek)
│   └── rag/               # RAG 检索 (ChromaDB + SimpleSearcher)
├── data/                  # 古籍 JSONL + ChromaDB + 题库 + 命例
└── netlify.toml           # Netlify 部署配置 (base=web/)
```

---

## 开发里程碑

### 2026-06-01 ~ 06-04 · 第一阶段 MVP
- [x] 排盘核心引擎 (lunar-python)
- [x] 五大类架构落地：命理/择吉/风水/学堂/典籍
- [x] 前端所有页面 + 古风 UI + PWA 支持
- [x] GitHub 仓库建立 + Netlify/Railway 部署配置

### 2026-06-05 · UI 重设计 Phase 1
- [x] 3 Tab 导航 → 4 Tab 导航 (今日/排盘/学堂/我的)
- [x] Calendar Hero + 禅意动画
- [x] 宣纸纹理 + 鎏金分割线 + 暖色卡片

### 2026-06-06 ~ 06-09 · v0.2→v0.3 核心功能补全
- [x] 排盘页大升级：公历/农历切换 + 精确时间 + 档案导入 + 经典命例 + 功能引流卡
- [x] 周易占卜重写：方法区分 + 五行调和 + 具体举措
- [x] 莫兰迪五行色卡 + 玄学 UI 隐性规范 (去煞圆角/三才步长/色克制/对称平衡)
- [x] 首页历史命例点击跳转排盘（时柱自动推算）
- [x] Service Worker 缓存问题修复
- [x] Netlify 构建修复 (base 目录 + localStorage SSR 守卫)
- [ ] 学堂错题本 → "我的"页面联动验证
- [ ] 合婚/起名页面入口通路完善

---

## 关键决策记录

| 日期 | 决策 | 理由 |
|---|---|---|
| 06-01 | 排盘引擎选 lunar-python | sxtwl 在 Windows 编译困难 |
| 06-01 | 不做恐吓式算命 | 产品定位为学术工具 |
| 06-01 | AI 不碰排盘计算 | 排盘 100% 代码确定性算法 |
| 06-05 | 默认检索器用 SimpleSearcher v2 | ChromaDB 需要 ONNX，内存占用大 |
| 06-05 | BottomNav 保持 4 Tab | 合婚/起名通过排盘结果页引流 |
| 06-09 | 农历转换放后端 | 不引入前端 JS 农历库，保持 PWA 轻量 |
| 06-09 | 莫兰迪色系替代纯原色 | 低饱和度古典色保持高级感 |
| 06-09 | Service Worker 临时禁用 | 缓存锁死导致部署后用户看不到新版本 |

---

## 当前页面清单

| 路径 | 页面 | 底部导航 | 备注 |
|---|---|---|---|
| `/jinri` | 今日首页 | 🏮 Tab1 | Calendar Hero + 宜忌 + 古籍 + 命例 |
| `/paipan` | 八字排盘 | ☯ Tab2 | 核心功能，含公农历切换/档案导入/经典命例 |
| `/xuetang` | 学堂 | 📚 Tab3 | 断案录答题 + 教材章节 + 错题本 |
| `/my` | 我的 | ☰ Tab4 | 亲友档案库 + 错题本入口 + 设置 |
| `/mingli` | 命理 | — | 子Tab: 排盘/合婚/流年/起名 |
| `/hehun` | 合婚 | — | 独立页面，从排盘结果引流 |
| `/zhouyi` | 周易占卜 | — | 时间/随机起卦 + 五行调和 |
| `/fengshui` | 风水 | — | 八宅 + 九宫飞星 + 形煞 |
| `/dianji` | 典籍 | — | 古籍检索 + 历史命例 |
| `/yiji` | 黄历 | — | 完整老黄历 + 择吉 |
| `/duanan` | 断案录 | — | 独立答题页 |

---

## 已知问题 & 待办

- [ ] 学堂错题本 → "我的"页面错题计数联动验证
- [ ] Railway 后端尚未部署上线（目前依赖本地后端或无后端模式）
- [ ] iOS PWA 添加到桌面引导（已有横幅，需验证效果）
- [ ] 流年/流月前端展示页未完成
- [ ] 穷通宝鉴原始文本已下载未清洗
- [ ] Service Worker 等部署稳定后重新启用
- [ ] 合婚/起名功能入口虽已有引流卡但缺少完整 UI 打磨

---

## Claude Code 使用约定

1. **每次开发前先读本文件**，了解当前版本和上下文
2. **重大改动后更新本文件**，记录日期和决策理由
3. **遵守 `CLAUDE.md` 的红线**，尤其是 AI 不排盘、古籍必须标出处
4. **玄学 UI 规范**：去煞圆角、三才步长、莫兰迪五行色、对称平衡、大象无形
5. **Git commit 前**：检查 TypeScript 编译无错误、构建通过
