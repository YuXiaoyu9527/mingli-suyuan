"use client";

import { useState, useEffect } from "react";
import { getDailyAlignment } from "@/lib/api";
import Link from "next/link";

const WX_MAP: Record<string, string> = { "金":"Metal","木":"Wood","水":"Water","火":"Fire","土":"Earth" };

export default function DailyPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDailyAlignment().then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-center text-text-muted pt-20">Loading today's alignment...</div>;
  if (!data) return <div className="p-6 text-center text-text-muted pt-20">Could not load data.</div>;

  return (
    <div className="p-6 min-h-dvh space-y-5 max-w-sm mx-auto">
      <header className="text-center pt-8 pb-4">
        <Link href="/" className="text-xs text-text-muted hover:text-text-secondary">← Back</Link>
        <h1 className="text-2xl font-[var(--font-display)] text-[var(--color-accent)] mt-2">Today's Alignment</h1>
        <p className="text-sm text-text-secondary mt-1">{data.day_ganzhi} Day · {data.week}</p>
      </header>

      {data.daily_tips ? (
        <div className="space-y-4 anim-stagger">
          <div className="card-accent text-center">
            <p className="text-4xl mb-2">{data.daily_tips?.wear_colors?.[0] === "红" ? "🔥" : "💧"}</p>
            <p className="text-lg font-bold">Colors: {data.daily_tips.wear_colors?.join(", ")}</p>
            <p className="text-xs text-text-muted mt-1">{data.daily_tips.wear_detail}</p>
          </div>
          <div className="card">
            <p className="text-sm font-bold mb-2">Today's Guidance</p>
            <p className="text-sm text-text-secondary">Do: {data.daily_tips.suggest_do}</p>
            <p className="text-sm text-text-secondary mt-1">Avoid: {data.daily_tips.suggest_avoid}</p>
            <p className="text-xs text-text-muted mt-2">Lucky Direction: {data.daily_tips.lucky_direction}</p>
          </div>
          {data.daily_tips.daily_quote && (
            <div className="card">
              <p className="text-xs text-text-muted italic">&ldquo;{data.daily_tips.daily_quote}&rdquo;</p>
            </div>
          )}
        </div>
      ) : (
        <div className="card text-center text-text-secondary text-sm">
          Enter your birth date on the home page first to get personalized daily alignment.
        </div>
      )}
    </div>
  );
}
