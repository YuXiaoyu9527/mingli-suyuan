/**
 * 后端 API 调用层
 *
 * 自动检测环境：
 * - 本地开发（localhost）→ http://localhost:8000
 * - 线上部署（Netlify）→ Railway 后端 URL
 * - 手机局域网测试 → 当前 host:8000
 */

// 生产环境后端地址（Railway 部署后生成）
const PRODUCTION_API = "https://mingli-suyuan-production.up.railway.app";

const getApiBase = () => {
  if (typeof window === "undefined") {
    // 服务端渲染：如果是生产构建用 Railway，否则用本地
    if (process.env.NODE_ENV === "production") return PRODUCTION_API;
    return "http://localhost:8000";
  }

  const host = window.location.hostname;
  // 本地开发
  if (host === "localhost" || host === "127.0.0.1") {
    return "http://localhost:8000";
  }
  // Netlify 部署的域名 → 用 Railway
  if (host.includes("netlify.app")) {
    return PRODUCTION_API;
  }
  // 局域网手机测试
  return `http://${host}:8000`;
};

export function getApiUrl() {
  return getApiBase();
}

async function fetchAPI(path: string, options?: RequestInit) {
  const url = `${getApiBase()}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

// ===== 排盘 =====
export interface PaipanParams {
  year: number; month: number; day: number; hour: number; minute: number; gender: string;
}
export async function paipan(params: PaipanParams) {
  return fetchAPI("/api/paipan", { method: "POST", body: JSON.stringify(params) });
}

// ===== 简批 =====
export interface JianpiParams extends PaipanParams { use_ai?: boolean; }
export async function jianpi(params: JianpiParams) {
  return fetchAPI("/api/jianpi", { method: "POST", body: JSON.stringify(params) });
}

// ===== 古籍检索 =====
export async function searchAncient(query: string, topK = 5, source?: string) {
  return fetchAPI("/api/search", { method: "POST", body: JSON.stringify({ query, top_k: topK, source }) });
}

// ===== 断案录 =====
export async function askMentor(question: string, studentAnswer: string, correctAnswer: string) {
  return fetchAPI("/api/mentor", { method: "POST", body: JSON.stringify({ question, student_answer: studentAnswer, correct_answer: correctAnswer }) });
}

// ===== 获取题库 =====
export async function getQuiz(chapter?: string) {
  return fetchAPI("/api/quiz", { method: "POST", body: JSON.stringify({ chapter: chapter || null }) });
}

// ===== 校验答案 =====
export async function checkAnswer(id: string, answer: number) {
  return fetchAPI("/api/quiz/check", { method: "POST", body: JSON.stringify({ id, answer }) });
}

// ===== 历史命例 =====
export async function getMingli(pattern?: string, search?: string) {
  return fetchAPI("/api/mingli", { method: "POST", body: JSON.stringify({ pattern: pattern || null, search: search || null }) });
}

// ===== 择吉 =====
export async function searchZeji(activity: string, days = 90) {
  return fetchAPI("/api/zeji", { method: "POST", body: JSON.stringify({ activity, days }) });
}

// ===== 今日宜忌 =====
export interface YijiParams {
  year?: number; month?: number; day?: number; hour?: number; minute?: number; gender?: string;
}
export async function getYiji(params?: YijiParams) {
  return fetchAPI("/api/yiji", { method: "POST", body: JSON.stringify(params || {}) });
}

// ===== 古籍来源列表 =====
export async function getSources() {
  return fetchAPI("/api/sources");
}
