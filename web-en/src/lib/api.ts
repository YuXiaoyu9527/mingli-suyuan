/** API helpers — points to shared backend */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI(path: string, body?: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

/** Full BaZi analysis: chart + pattern + useful god + AI interpretation */
export function getBlueprint(params: {
  year: number; month: number; day: number; hour: number;
  minute?: number; gender?: string; city?: string;
}) {
  return fetchAPI("/api/full-analysis", { ...params, language: "en", calendar_type: "solar" } as Record<string, unknown>);
}

/** Daily almanac + personalized tips */
export function getDailyAlignment(params?: {
  year?: number; month?: number; day?: number; hour?: number; gender?: string;
}) {
  return fetchAPI("/api/yiji", (params || {}) as Record<string, unknown>);
}

/** Search ancient texts */
export function searchAncient(query: string, topK = 3) {
  return fetchAPI("/api/search", { query, top_k: topK });
}

/** Classical → modern Chinese translation */
export function translateClassical(text: string) {
  return fetchAPI("/api/translate-classical", { text });
}
