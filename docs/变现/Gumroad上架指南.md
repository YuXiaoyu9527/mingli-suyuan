# Gumroad 上架指南 — 命理溯源源码

> 跟着做就能上架，30 分钟内搞定

---

## 一、产品定位

```
卖给谁：  想快速搭建玄学/占卜网站的独立开发者、小团队
卖什么：  完整源码 + 部署指南 + 30 天邮件支持
卖多少钱：$49（基础版）/ $79（含商业授权）
```

---

## 二、Gumroad 产品页面文案（直接复制粘贴）

### Title
```
DestinyScroll — Complete Chinese Fortune-Telling Web App (Next.js + Python)
```

### Subtitle (one-liner)
```
Source code for a production-ready PWA with BaZi charting, I-Ching divination, ancient text search, and AI interpretation. Built with Next.js 16 + FastAPI + lunar-python.
```

### Description
```markdown
## What You Get

A complete, ready-to-deploy fortune-telling / traditional Chinese culture learning web app. NOT a demo — this is a full product with 11 pages, a Python BaZi calculation engine, 4,800+ ancient text records, and beautiful morandi-color UI.

### Tech Stack
- **Frontend:** Next.js 16 + React 19 + Tailwind CSS v4 + Framer Motion
- **Backend:** FastAPI + Python 3.13 + lunar-python (deterministic chart engine)
- **AI:** DeepSeek-V4 (OpenAI-compatible API)
- **Search:** ChromaDB vector search + keyword fallback
- **Deploy:** Netlify (frontend) + Railway (backend) configs included

### Features (11 Pages)

| Page | Description |
|------|-------------|
| 🏮 Today | Calendar hero with seasonal color shift, daily almanac, ancient text of the day |
| ☯ BaZi Chart | Four Pillars (year/month/day/hour) with True Solar Time correction, solar/lunar calendar toggle |
| 🔮 I-Ching | 64 hexagrams with spring-animation, body-use-shengke analysis, Five-Element harmony advice (what colors to wear, what items to carry) |
| 📚 Academy | Quiz-based learning with chapter unlocking, AI mentor, wrong-answer book |
| 👤 Profile | Saved birth charts, local storage, one-tap chart lookup |
| 💑 Compatibility | Four-dimension couple matching (animal zodiac, day branch, five elements, ten gods) |
| ✏️ Naming | Baby name suggestions based on parents' BaZi useful gods, with classical poetry sources |
| 🏠 Feng Shui | Eight Mansions analysis, Nine Star layout, missing-corner detection |
| 📖 Ancient Texts | Full-text search across 4,800+ records from San Ming Tong Hui, Di Tian Sui, etc. |
| 📅 Almanac | Complete Chinese almanac with auspicious/inauspicious activities, hourly luck |
| 🎴 Case Studies | Historical figure birth charts (Li Bai, Su Shi, Zhuge Liang, etc.) |

### Design Highlights
- Hand-drawn paper texture background
- Morandi Five-Element color system (low-saturation classical palette)
- Four-Symbol (Si Xiang) spatial layout — Azure Dragon, Vermilion Bird, White Tiger, Black Tortoise
- 24 Solar Terms auto-color-shift — the hero character changes color with the seasons
- De-sha rounded corners (16px+) — no sharp edges, intentional feng-shui of UI

### What's in the ZIP
```
mingli-suyuan/
├── web/                  # Next.js frontend (11 pages)
├── api/                  # FastAPI backend (8 engines)
├── data/                 # 4,800+ ancient texts + quiz bank + case studies
├── CLAUDE.md             # Project constitution (AI guidelines)
├── SETUP_GUIDE.md        # Step-by-step deployment guide (English)
├── netlify.toml          # Netlify deploy config
├── railway.toml          # Railway deploy config
├── requirements.txt      # Python dependencies
└── README_EN.md          # English documentation
```

### Requirements
- Node.js 18+
- Python 3.11+
- (Optional) DeepSeek API key for AI interpretation

### License
- **$49 — Personal License:** Use for one personal project, modify freely
- **$79 — Commercial License:** Use for client work, SaaS, or resell as part of your service

### Support
30-day email support. I'll help you get it running on your machine.

### Refund Policy
14-day money-back guarantee. If you can't get it running, I'll refund you — no questions asked.
```

### Product Image Suggestions
```
至少准备 5 张截图（用你手机录屏里最好看的几帧）：
1. 今日首页 Calendar Hero（显示节气+四宫格）         ← 封面图
2. 排盘四柱五色八字特写
3. 周易占卜六条爻线动画定格
4. 五行调和卡片（穿衣颜色+随身物品）
5. 古籍搜索搜索结果

把截图拖到/docs/gumroad_screenshots/ 文件夹里
```

---

## 三、定价

| 档位 | 价格 | 内容 |
|---|---|---|
| Personal | **$49** | 源码 + 部署指南 + 30天邮件支持 |
| Commercial | **$79** | 以上 + 可用在客户项目/SaaS 中 |

**为什么 $49 而不是 $29？**
- 你的产品有 11 个页面+8 个 Python 引擎+4800 条数据，不是模板
- Gumroad 上同类"完整 App 源码"定价在 $39-99
- FateTell 参考：他们的 B2B 授权是 $499/年，$49 已经是白菜价
- 可以设置首周 30% off = $34.30，测试价格弹性

---

## 四、Gumroad 操作步骤

```
1. 打开 gumroad.com → 注册账号
2. 点 Products → New Product
3. 选 "Digital product"
4. 粘贴上面的 Title / Description
5. 上传 5 张截图
6. 设置价格 $49
7. Publish → 获得产品链接（如 https://xxx.gumroad.com/l/destinyscroll）

整个流程 15 分钟
```

---

## 五、发布后

```
□ 把 Gumroad 链接发到你的抖音/即刻/Twitter 简介里
□ 在 Product Hunt 上提交（选 "Digital Product" 分类）
□ 在 Reddit r/SideProject / r/webdev 上发帖（"I built a Chinese divination app with AI"）
□ Fiverr gig 里引用 Gumroad 链接作为 portfolio
```
