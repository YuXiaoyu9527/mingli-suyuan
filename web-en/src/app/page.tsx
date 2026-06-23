"use client";

import { useState } from "react";
import { getBlueprint } from "@/lib/api";
import { Sparkles, ChevronRight, Shirt, MapPin, Compass } from "lucide-react";

const WX_COLORS: Record<string, { hex: string; emoji: string; trait: string }> = {
  Wood: { hex: "#7A9A7E", emoji: "🌿", trait: "Growth-oriented, creative, flexible" },
  Fire: { hex: "#C06050", emoji: "🔥", trait: "Passionate, charismatic, energetic" },
  Earth: { hex: "#C4A882", emoji: "🏔️", trait: "Grounded, nurturing, stable" },
  Metal: { hex: "#B8A88A", emoji: "⚜️", trait: "Disciplined, principled, refined" },
  Water: { hex: "#5B7B8A", emoji: "💧", trait: "Intuitive, wise, adaptable" },
};

const WX_ADVICE: Record<string, { wear: string; avoid: string; direction: string; action: string }> = {
  Wood: { wear: "Green, teal, light blue", avoid: "White, silver (Metal weakens Wood)", direction: "East", action: "Start something new today. Make a long-term plan. Spend time in nature." },
  Fire: { wear: "Red, purple, warm orange", avoid: "Black, dark blue (Water extinguishes Fire)", direction: "South", action: "Socialize. Make that call you've been putting off. Share your ideas publicly." },
  Earth: { wear: "Yellow, brown, beige", avoid: "Green (Wood drains Earth)", direction: "Southwest", action: "Ground yourself. Do one practical task well. Help someone without expecting return." },
  Metal: { wear: "White, silver, light grey", avoid: "Red (Fire melts Metal)", direction: "Northwest", action: "Declutter your space. Make a decision you've been avoiding. Set clear boundaries." },
  Water: { wear: "Black, navy, deep blue", avoid: "Yellow, brown (Earth blocks Water)", direction: "North", action: "Meditate. Journal. Let your intuition guide decisions today. Rest is productive." },
};

export default function Home() {
  const [form, setForm] = useState({ year: 1990, month: 5, day: 20, hour: 12, gender: "Male" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true); setError("");
    try {
      const data = await getBlueprint({
        year: form.year, month: form.month, day: form.day, hour: form.hour,
        gender: form.gender === "Male" ? "男" : "女",
      });
      setResult(data);
    } catch (e: any) {
      setError("Could not connect to server. Please try again.");
    }
    setLoading(false);
  };

  const p = result?.paipan;
  const g = result?.geju;
  const y = result?.yongshen;
  const rizhuWx = p?.rizhu_wuxing || "";
  // Map Chinese wuxing to English
  const wxMap: Record<string, string> = { "金": "Metal", "木": "Wood", "水": "Water", "火": "Fire", "土": "Earth" };
  const element = wxMap[rizhuWx] || "Unknown";
  const wxInfo = WX_COLORS[element] || WX_COLORS.Water;
  const mainYong = y?.recommended?.[0] ? wxMap[y.recommended[0]] || "" : "";
  const advice = WX_ADVICE[element] || WX_ADVICE.Water;

  return (
    <div className="p-6 min-h-dvh flex flex-col">
      {/* Header */}
      <header className="text-center pt-8 pb-6">
        <h1 className="text-4xl font-[var(--font-display)] text-[var(--color-accent)] tracking-wide">
          DestinyScroll
        </h1>
        <p className="text-text-secondary text-sm mt-2">
          Ancient wisdom for modern self-discovery
        </p>
      </header>

      {/* Input Form (before result) */}
      {!result && (
        <div className="flex-1 flex flex-col justify-center max-w-sm mx-auto w-full space-y-5">
          <div className="text-center mb-2">
            <p className="text-2xl font-bold">Discover Your Element</p>
            <p className="text-text-secondary text-sm mt-2">
              Based on BaZi — a 1,000-year-old Chinese system for understanding personality, timing, and life path.
            </p>
          </div>

          <div className="card space-y-4">
            <div className="grid grid-cols-3 gap-3">
              {[
                { k: "year", label: "Year", ph: "1990" },
                { k: "month", label: "Month", ph: "5" },
                { k: "day", label: "Day", ph: "20" },
              ].map(({ k, label, ph }) => (
                <div key={k}>
                  <label className="text-[11px] text-text-muted uppercase tracking-wider">{label}</label>
                  <input
                    type="number" value={(form as any)[k]}
                    onChange={e => setForm({ ...form, [k]: +e.target.value })}
                    className="w-full mt-1 text-center" placeholder={ph}
                  />
                </div>
              ))}
            </div>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="text-[11px] text-text-muted uppercase tracking-wider">Birth Hour</label>
                <input
                  type="number" value={form.hour} min={0} max={23}
                  onChange={e => setForm({ ...form, hour: +e.target.value })}
                  className="w-full mt-1 text-center" placeholder="12"
                />
              </div>
              <div>
                <label className="text-[11px] text-text-muted uppercase tracking-wider">Gender</label>
                <select
                  value={form.gender}
                  onChange={e => setForm({ ...form, gender: e.target.value })}
                  className="w-full mt-1"
                >
                  <option>Male</option>
                  <option>Female</option>
                </select>
              </div>
            </div>
          </div>

          <button onClick={handleSubmit} disabled={loading} className="btn-primary w-full">
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-5 h-5 border-2 border-[#1A1520]/30 border-t-[#1A1520] rounded-full animate-spin" />
                Reading your stars...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles size={18} /> Reveal My Element
              </span>
            )}
          </button>
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        </div>
      )}

      {/* Result */}
      {result && p && (
        <div className="flex-1 max-w-sm mx-auto w-full space-y-5 anim-stagger">
          {/* Element Card */}
          <div className="card-accent text-center">
            <p className="text-5xl mb-3">{wxInfo.emoji}</p>
            <p className="text-text-secondary text-xs uppercase tracking-[0.2em]">Your Element</p>
            <h2 className="text-3xl font-[var(--font-display)] mt-1" style={{ color: wxInfo.hex }}>
              {element}
            </h2>
            <p className="text-text-secondary text-sm mt-2">{wxInfo.trait}</p>
            {g?.pattern && (
              <p className="text-xs text-text-muted mt-2">
                BaZi Pattern: <span className="text-[var(--color-accent)]">{g.pattern}</span>
                &nbsp;·&nbsp;
                {y?.wangshuai && <span>{y.wangshuai}</span>}
              </p>
            )}
          </div>

          {/* Personality Snapshot */}
          <div className="card">
            <h3 className="text-sm font-bold flex items-center gap-2 mb-3">
              <Sparkles size={14} className="text-[var(--color-accent)]" /> Your Blueprint
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed">
              {g?.analysis ? g.analysis.slice(0, 300) + (g.analysis.length > 300 ? "..." : "") : "Your chart reveals a unique combination of elements that shapes your personality, strengths, and life path."}
            </p>
            {y?.analysis && (
              <p className="text-sm text-text-secondary leading-relaxed mt-2">
                {y.analysis.slice(0, 250) + (y.analysis.length > 250 ? "..." : "")}
              </p>
            )}
          </div>

          {/* Today's Alignment */}
          <div className="card" style={{ borderColor: "rgba(201,169,110,0.3)" }}>
            <h3 className="text-sm font-bold flex items-center gap-2 mb-3">
              <Compass size={14} className="text-[var(--color-accent)]" /> Today's Alignment
            </h3>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Shirt size={16} className="text-text-muted mt-0.5" />
                <div>
                  <p className="text-xs text-text-muted">Wear</p>
                  <p className="text-sm">{advice.wear}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <MapPin size={16} className="text-text-muted mt-0.5" />
                <div>
                  <p className="text-xs text-text-muted">Favorable Direction</p>
                  <p className="text-sm">{advice.direction}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <ChevronRight size={16} className="text-text-muted mt-0.5" />
                <div>
                  <p className="text-xs text-text-muted">Today's Guidance</p>
                  <p className="text-sm">{advice.action}</p>
                </div>
              </div>
            </div>
            {mainYong && (
              <div className="mt-3 pt-3 border-t border-[var(--color-border)]">
                <p className="text-xs text-text-muted">
                  Your chart favors <span className="text-[var(--color-accent)]">{mainYong}</span> element.
                  Avoid <span className="text-red-400/70">{y?.jishen?.map((j: string) => wxMap[j] || j).join(", ")}</span>.
                </p>
              </div>
            )}
          </div>

          {/* Source */}
          {result.ancient_refs?.length > 0 && (
            <div className="card">
              <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider mb-2">
                Ancient Source
              </h3>
              <p className="text-xs text-text-secondary italic">
                &ldquo;{result.ancient_refs[0]?.content?.slice(0, 200)}...&rdquo;
              </p>
              <p className="text-[10px] text-text-muted mt-1">
                — {result.ancient_refs[0]?.source_name}, {result.ancient_refs[0]?.volume}
              </p>
            </div>
          )}

          {/* Try Again */}
          <button onClick={() => { setResult(null); setError(""); }} className="w-full py-3 text-sm text-text-muted hover:text-text-secondary transition-colors">
            ← Enter a different birth date
          </button>

          <p className="text-center text-[10px] text-text-muted pb-4">
            For cultural reference and self-discovery only. Not a substitute for professional advice.
          </p>
        </div>
      )}
    </div>
  );
}
