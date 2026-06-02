/**
 * 后端 API 调用层
 * 连接 FastAPI 后端 (默认 http://localhost:8000)
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI(path: string, options?: RequestInit) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ===== 排盘 =====

export interface PaipanParams {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  gender: string;
}

export async function paipan(params: PaipanParams) {
  return fetchAPI("/api/paipan", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

// ===== 简批（排盘 + 检索 + AI） =====

export interface JianpiParams extends PaipanParams {
  use_ai?: boolean;
}

export async function jianpi(params: JianpiParams) {
  return fetchAPI("/api/jianpi", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

// ===== 古籍检索 =====

export async function searchAncient(query: string, topK = 5, source?: string) {
  return fetchAPI("/api/search", {
    method: "POST",
    body: JSON.stringify({ query, top_k: topK, source }),
  });
}

// ===== 断案录导师 =====

export async function askMentor(
  question: string,
  studentAnswer: string,
  correctAnswer: string
) {
  return fetchAPI("/api/mentor", {
    method: "POST",
    body: JSON.stringify({
      question,
      student_answer: studentAnswer,
      correct_answer: correctAnswer,
    }),
  });
}

// ===== 今日宜忌 =====

export interface YijiParams {
  year?: number;
  month?: number;
  day?: number;
  hour?: number;
  minute?: number;
  gender?: string;
}

export async function getYiji(params?: YijiParams) {
  return fetchAPI("/api/yiji", {
    method: "POST",
    body: JSON.stringify(params || {}),
  });
}

// ===== 断案录题库 =====

export async function getQuiz(chapter?: string) {
  return fetchAPI("/api/quiz", {
    method: "POST",
    body: JSON.stringify({ chapter: chapter || null }),
  });
}

export async function checkAnswer(id: string, answer: number) {
  return fetchAPI("/api/quiz/check", {
    method: "POST",
    body: JSON.stringify({ id, answer }),
  });
}

// ===== 历史命例 =====

export async function getMingli(pattern?: string, search?: string) {
  return fetchAPI("/api/mingli", {
    method: "POST",
    body: JSON.stringify({ pattern: pattern || null, search: search || null }),
  });
}

// ===== 择吉搜索 =====

export async function searchZeji(activity: string, days = 90) {
  return fetchAPI("/api/zeji", {
    method: "POST",
    body: JSON.stringify({ activity, days }),
  });
}

// ===== 古籍来源列表 =====

export async function getSources() {
  return fetchAPI("/api/sources");
}
