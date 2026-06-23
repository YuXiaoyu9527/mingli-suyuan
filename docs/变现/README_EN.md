# DestinyScroll — Chinese Fortune-Telling Learning Tool

> A production-ready PWA for traditional Chinese culture study: BaZi charting, I-Ching divination, ancient text search, and AI-powered interpretation. Built by one person + AI in 15 days.

---

## Quick Start (5 Minutes)

### Prerequisites
- **Node.js 18+** ([nodejs.org](https://nodejs.org))
- **Python 3.11+** ([python.org](https://python.org))

### 1. Install Backend Dependencies
```bash
# From project root
pip install lunar-python chromadb onnxruntime fastapi uvicorn
```

### 2. Install Frontend Dependencies
```bash
cd web
npm install
```

### 3. Start Backend
```bash
# From project root
python -m uvicorn api.server:app --port 8000
```

### 4. Start Frontend
```bash
cd web
npm run dev
```

Open **http://localhost:3000** in your browser. Done.

### Optional: AI Interpretation
Create a `.env` file in the project root:
```
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```
The AI-powered BaZi interpretation and I-Ching mentor will then work automatically.

---

## What's Inside

### Frontend (web/)
| Path | Description |
|------|-------------|
| `/jinri` | Home page — daily almanac, seasonal color hero, Si-Xiang tool grid |
| `/paipan` | BaZi (Four Pillars) chart — solar/lunar toggle, minute-precision input, classic case quick-fill |
| `/zhouyi` | I-Ching divination — time/random method, hexagram animation, Five-Element harmony guide |
| `/xuetang` | Learning academy — quiz chapters, AI mentor, wrong-answer review |
| `/my` | User profile — saved charts, settings |
| `/hehun` | Couple compatibility — 4-dimension matching |
| `/mingli` | Advanced — naming engine, yearly luck analysis |
| `/dianji` | Ancient text search — 4,800+ records |
| `/fengshui` | Feng Shui analysis — Eight Mansions, Nine Stars |
| `/yiji` | Full almanac — hourly luck, auspicious activities |

### Backend (api/)
| Engine | File | What it does |
|--------|------|-------------|
| BaZi Engine | `api/paipan/engine.py` | Deterministic Four Pillars calculation via lunar-python |
| Pattern Engine | `api/paipan/geju.py` | Automatically identifies chart patterns (正格/变格/从格) |
| Useful God Engine | `api/paipan/yongshen.py` | Recommends balancing elements |
| Shen Sha Engine | `api/paipan/shensha.py` | Calculates spirit/villain stars |
| Da Yun Engine | `api/paipan/dayun.py` | 10-year luck cycle calculation |
| I-Ching Engine | `api/paipan/zhouyi.py` | 64 hexagrams with body-use-shengke analysis |
| Naming Engine | `api/paipan/qiming.py` | Baby name suggestions from classical poetry |
| Compatibility Engine | `api/paipan/hehun.py` | 4-dimension couple matching |
| Feng Shui Engine | `api/paipan/fengshui.py` | Eight Mansions + Nine Star analysis |
| Zeji Engine | `api/paipan/zeji.py` | Auspicious date search |
| True Solar Time | `api/paipan/truesolar.py` | City-based solar time correction |
| RAG Search | `api/rag/searcher.py` | ChromaDB vector search over ancient texts |
| AI Interpreter | `api/ai/interpreter.py` | DeepSeek-V4 integration |

### Data (data/)
- `cleaned/` — 4 cleaned classical texts (JSON format)
- `mingli_cases.jsonl` — Historical figure birth charts
- `quiz_cases.jsonl` — Quiz question bank
- `learning_chapters.json` — Academy course structure
- `chroma_db/` — Vector database index

---

## Deployment

### Frontend → Netlify
The `netlify.toml` is already configured. Connect your GitHub repo to Netlify and it auto-deploys.

### Backend → Railway
The `railway.toml` is ready. Run `railway up` from project root.

### PWA
The app works as a PWA out of the box. Users can "Add to Home Screen" on iOS/Android for a native-app experience.

---

## Design Philosophy

This app follows "invisible feng-shui" principles — the spiritual intent is in the code, not the decoration:

- **De-sha corners:** All cards use 16px+ border radius (no sharp edges = no "sha" energy)
- **Three-Cai spacing:** Key margins use multiples of 3 (p-3, p-6, p-12) — echoing Heaven-Earth-Human trinity
- **Morandi Five-Element palette:** Low-saturation classical colors for wood/fire/earth/metal/water — never fluorescent
- **24 Solar Terms color shift:** The hero character changes color with the seasons automatically
- **Si-Xiang spatial grid:** Four tool cards positioned as Azure Dragon (E) / Vermilion Bird (S) / White Tiger (W) / Black Tortoise (N)

---

## Customization

### Change Colors
Edit `web/src/app/globals.css` — all design tokens are CSS variables:
```css
--color-accent: #B33A2E;      /* Main red */
--color-gold: #B8860B;        /* Gold border */
--color-bg: #FDFCF8;          /* Paper background */
--color-wx-wood: #7A9A7E;     /* Wood element green */
--color-wx-fire: #B5544A;     /* Fire element red */
--color-wx-earth: #C4A882;    /* Earth element amber */
--color-wx-metal: #B8A88A;    /* Metal element gold */
--color-wx-water: #5B7B8A;    /* Water element blue */
```

### Add New Features
Read `CLAUDE.md` first — it contains the project constitution, AI usage rules, and design guidelines. All AI-generated content must cite its ancient text source. All BaZi calculations must be done by code, never by AI.

---

## Support

- 30-day email support included with purchase
- 14-day money-back guarantee
- Contact: your email here

---

## License

This product comes with two license options:
- **Personal ($49):** Use for one personal project. Modify freely.
- **Commercial ($79):** Use for client projects, SaaS products, or resell as part of your service.

---

*Built with Claude Code AI assistant. 15 days from idea to launch.*
