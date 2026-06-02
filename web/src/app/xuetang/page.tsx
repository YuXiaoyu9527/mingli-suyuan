"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { checkAnswer, askMentor } from "@/lib/api";
import { Loader2, BookOpen, ChevronRight, Lock, CheckCircle, ArrowLeft, Swords, Star } from "lucide-react";

interface Chapter {
  id: string; title: string; subtitle: string; order: number;
  unlock_requires: string | null; question_count: number; pass_score: number;
}

interface ChapterDetail {
  id: string; title: string; subtitle: string; pass_score: number;
  content: { type: string; text: string; source?: string }[];
  questions: QuizItem[];
}

interface QuizItem {
  id: string; title: string; difficulty: number;
  story: string; question: string;
  options: { label: string; text: string }[];
}

export default function XuetangPage() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [chapterDetail, setChapterDetail] = useState<ChapterDetail | null>(null);
  const [loading, setLoading] = useState(true);
  // 进度
  const [passed, setPassed] = useState<Record<string, boolean>>({});
  // 测验状态
  const [quizMode, setQuizMode] = useState(false);
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizChecked, setQuizChecked] = useState<Record<number, boolean>>({});
  const [quizCorrectText, setQuizCorrectText] = useState<Record<number, string>>({});
  const [quizResult, setQuizResult] = useState<{ correct: number; total: number; passed: boolean } | null>(null);
  const [mentorMsg, setMentorMsg] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("xuetang_passed");
    if (saved) setPassed(JSON.parse(saved));
    loadChapters();
  }, []);

  const loadChapters = async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/xuetang");
      const data = await resp.json();
      setChapters(data.chapters || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const loadChapter = async (chId: string) => {
    setLoading(true);
    try {
      const resp = await fetch(`http://localhost:8000/api/xuetang/${chId}`);
      const data = await resp.json();
      setChapterDetail(data);
      setQuizMode(false);
      setQuizIdx(0);
      setQuizAnswers({});
      setQuizChecked({});
      setQuizCorrectText({});
      setQuizResult(null);
      setMentorMsg("");
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const isUnlocked = (ch: Chapter) => {
    if (!ch.unlock_requires) return true;
    return passed[ch.unlock_requires] === true;
  };

  const handleAnswer = async (optIdx: number) => {
    if (quizChecked[quizIdx] !== undefined) return;

    const q = chapterDetail!.questions[quizIdx];
    setQuizAnswers({ ...quizAnswers, [quizIdx]: optIdx });

    try {
      const result = await checkAnswer(q.id, optIdx);
      const correct = result.correct;
      setQuizChecked({ ...quizChecked, [quizIdx]: correct });
      if (result.correct_text) {
        setQuizCorrectText({ ...quizCorrectText, [quizIdx]: result.correct_text });
      }

      if (!correct) {
        try {
          const mentor = await askMentor(
            `${q.story}\n\n${q.question}`,
            q.options[optIdx].text,
            result.correct_text || q.options[result.correct_answer]?.text || "",
          );
          setMentorMsg(mentor.hint || "");
        } catch {}
      } else {
        setMentorMsg("");
      }
    } catch {}
  };

  const finishQuiz = () => {
    const total = chapterDetail!.questions.length;
    const correct = Object.values(quizChecked).filter(Boolean).length;
    const passed_quiz = correct >= chapterDetail!.pass_score;

    setQuizResult({ correct, total, passed: passed_quiz });

    if (passed_quiz) {
      const newPassed = { ...passed, [chapterDetail!.id]: true };
      setPassed(newPassed);
      localStorage.setItem("xuetang_passed", JSON.stringify(newPassed));
    }
  };

  // ===== 章节列表视图 =====
  if (!chapterDetail) {
    return (
      <div className="flex flex-col min-h-dvh pb-20">
        <header className="px-5 pt-10 pb-4">
          <h1 className="text-2xl text-dao-ink font-[family-name:var(--font-display)] tracking-wider">
            命理学堂
          </h1>
          <p className="text-dao-aged text-sm mt-1">从零学八字 · 教材+测验 · 通关解锁</p>
        </header>

        <div className="px-5 flex-1 space-y-3">
          {loading && (
            <div className="flex justify-center py-12">
              <Loader2 size={28} className="animate-spin text-dao-gold" />
            </div>
          )}

          {chapters.map((ch) => {
            const unlocked = isUnlocked(ch);
            return (
              <button key={ch.id} disabled={!unlocked}
                onClick={() => loadChapter(ch.id)}
                className={`w-full text-left dao-card tap-active transition-all
                  ${!unlocked ? "opacity-50" : "hover:border-dao-gold/50"}`}>
                <div className="flex items-center gap-4">
                  {/* 图标 */}
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
                    ${passed[ch.id] ? "bg-dao-jade/20 text-dao-jade" :
                      unlocked ? "bg-dao-gold/10 text-dao-gold" : "bg-dao-paper-dark text-dao-aged"}`}>
                    {passed[ch.id] ? <CheckCircle size={22} /> :
                     unlocked ? <BookOpen size={22} /> : <Lock size={22} />}
                  </div>
                  {/* 信息 */}
                  <div className="flex-1">
                    <h3 className="text-base font-bold text-dao-ink">{ch.title}</h3>
                    <p className="text-xs text-dao-aged mt-0.5">{ch.subtitle}</p>
                    <div className="flex items-center gap-3 mt-1.5 text-[11px] text-dao-aged-light">
                      <span>{ch.question_count}道情景题</span>
                      <span>正确{ch.pass_score}题即通关</span>
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-dao-aged" />
                </div>
                {/* 进度条 */}
                {passed[ch.id] && (
                  <div className="mt-3 h-1 bg-dao-jade/20 rounded-full overflow-hidden">
                    <div className="h-full bg-dao-jade w-full rounded-full" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
        <BottomNav />
      </div>
    );
  }

  // ===== 章节详情视图 =====
  const q = chapterDetail.questions[quizIdx];
  const totalProgress = Object.keys(passed).length;
  const totalChapters = chapters.length;

  return (
    <div className="flex flex-col min-h-dvh pb-20">
      <header className="px-5 pt-6 pb-3">
        <div className="flex items-center gap-3">
          <button onClick={() => setChapterDetail(null)}
            className="text-dao-aged tap-active"><ArrowLeft size={20} /></button>
          <div className="flex-1">
            <h1 className="text-lg font-[family-name:var(--font-display)] text-dao-ink">
              {chapterDetail.title}
            </h1>
          </div>
          <button onClick={() => setQuizMode(!quizMode)}
            className={`text-xs px-3 py-1.5 rounded-full tap-active border
              ${quizMode ? "bg-dao-red text-white border-dao-red" : "bg-dao-paper-dark text-dao-ink-light border-dao-paper-darker"}`}>
            {quizMode ? "← 回教材" : "开始测验 →"}
          </button>
        </div>
        {/* 总进度 */}
        <div className="mt-2 flex items-center gap-2 text-[11px] text-dao-aged">
          <span>学习进度：{totalProgress}/{totalChapters}章</span>
          <div className="flex-1 h-1 bg-dao-paper-dark rounded-full overflow-hidden">
            <div className="h-full bg-dao-gold rounded-full" style={{width: `${(totalProgress/totalChapters)*100}%`}} />
          </div>
        </div>
      </header>

      <div className="px-5 flex-1">
        {!quizMode ? (
          // ===== 阅读模式 =====
          <div className="space-y-4 anim-enter">
            {chapterDetail.content.map((block, i) => {
              if (block.type === "heading") {
                return <h2 key={i} className="text-lg font-bold text-dao-ink mt-6 mb-2 font-[family-name:var(--font-display)]">{block.text}</h2>;
              }
              if (block.type === "quote") {
                return (
                  <div key={i} className="classical-quote text-sm">
                    <p>{block.text}</p>
                    {block.source && <p className="text-[10px] text-dao-aged mt-2">—— {block.source}</p>}
                  </div>
                );
              }
              return <p key={i} className="text-sm text-dao-ink-light leading-relaxed">{block.text}</p>;
            })}

            {/* 进入测验按钮 */}
            <div className="py-6 text-center">
              <button onClick={() => setQuizMode(true)}
                className="btn-dao flex items-center gap-2 mx-auto">
                <Swords size={16} /> 开始测验（{chapterDetail.questions.length}题）
              </button>
              <p className="text-[11px] text-dao-aged mt-2">正确{chapterDetail.pass_score}题即可通关</p>
            </div>
          </div>
        ) : quizResult ? (
          // ===== 测验结果 + 错题回顾 =====
          <div className="anim-enter space-y-4">
            {/* 分数卡片 */}
            <div className="text-center py-8 space-y-4">
              <div className={`w-20 h-20 rounded-full mx-auto flex items-center justify-center
                ${quizResult.passed ? "bg-dao-jade/20" : "bg-dao-red/10"}`}>
                <span className={`text-3xl font-bold ${quizResult.passed ? "text-dao-jade" : "text-dao-red"}`}>
                  {quizResult.correct}/{quizResult.total}
                </span>
              </div>
              <h2 className={`text-xl font-bold ${quizResult.passed ? "text-dao-jade" : "text-dao-red"}`}>
                {quizResult.passed ? "恭喜通关！" : "还需努力"}
              </h2>
              <p className="text-sm text-dao-aged">
                {quizResult.passed
                  ? "下一章已解锁，继续学习吧！"
                  : `需要正确${chapterDetail.pass_score}题才能通关`}
              </p>
            </div>

            {/* 逐题回顾 */}
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-dao-ink">答题回顾</h3>
              {chapterDetail.questions.map((q, i) => {
                const isRight = quizChecked[i] === true;
                const isWrong = quizChecked[i] === false;
                const userAnswer = quizAnswers[i];
                const userOption = userAnswer !== undefined ? q.options[userAnswer].text : "未作答";
                return (
                  <div key={i} className={`dao-card py-3 px-4 ${isRight ? "border-l-2 border-l-dao-jade" : isWrong ? "border-l-2 border-l-dao-red" : ""}`}>
                    <div className="flex items-start gap-2">
                      <span className={`text-xs font-bold mt-0.5 ${isRight ? "text-dao-jade" : isWrong ? "text-dao-red" : "text-dao-aged"}`}>
                        {isRight ? "✓" : isWrong ? "✗" : "○"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-dao-ink">{q.title}</p>
                        <p className="text-[11px] text-dao-aged mt-0.5">你的回答：{userOption}</p>
                        {isWrong && quizCorrectText[i] && (
                          <p className="text-[11px] text-dao-jade mt-0.5">正确答案：{quizCorrectText[i]}</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-3 justify-center pt-2">
              {!quizResult.passed && (
                <button onClick={() => {
                  setQuizMode(true); setQuizIdx(0); setQuizAnswers({});
                  setQuizChecked({}); setQuizResult(null); setMentorMsg("");
                }} className="px-4 py-2 bg-dao-red text-white rounded-lg text-sm tap-active">
                  重新测验
                </button>
              )}
              <button onClick={() => {
                setQuizMode(false); setQuizIdx(0); setQuizAnswers({});
                setQuizChecked({}); setQuizResult(null); setMentorMsg("");
              }} className="px-4 py-2 bg-dao-paper-dark rounded-lg text-sm tap-active">
                回教材再看一遍
              </button>
            </div>
          </div>
        ) : (
          // ===== 测验模式 =====
          <div className="space-y-4 anim-enter">
            {/* 进度 */}
            <div className="flex items-center justify-between text-xs text-dao-aged">
              <span>第 {quizIdx + 1}/{chapterDetail.questions.length} 题</span>
              <div className="flex gap-1">
                {chapterDetail.questions.map((_, i) => (
                  <div key={i} className={`w-2 h-2 rounded-full
                    ${quizChecked[i] === true ? "bg-dao-jade" :
                      quizChecked[i] === false ? "bg-dao-red" :
                      quizAnswers[i] !== undefined ? "bg-dao-gold" : "bg-dao-paper-darker"}`} />
                ))}
              </div>
              <span className="text-dao-gold">
                已对 {Object.values(quizChecked).filter(Boolean).length} 题
              </span>
            </div>

            {q && (
              <>
                {/* 题目 */}
                <div className="dao-card">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-dao-aged">{q.title}</span>
                    <span className="flex gap-0.5">
                      {[1,2,3].map(d => <Star key={d} size={10} className={d <= q.difficulty ? "fill-dao-gold text-dao-gold" : "text-dao-paper-darker"} />)}
                    </span>
                  </div>
                  <p className="text-sm text-dao-ink-light leading-relaxed whitespace-pre-line">{q.story}</p>
                </div>

                {/* 问题 */}
                <div className="dao-card" style={{ borderColor: "rgba(201,169,110,0.3)" }}>
                  <p className="text-sm font-bold text-dao-ink mb-3">❓ {q.question}</p>
                  <div className="space-y-2">
                    {q.options.map((opt, i) => {
                      const checked = quizChecked[quizIdx];
                      const isSelected = quizAnswers[quizIdx] === i;
                      let style = "border-dao-paper-darker";
                      if (checked !== undefined && isSelected) {
                        style = checked ? "border-dao-jade bg-dao-jade/5" : "border-dao-red bg-dao-red/5";
                      } else if (!isSelected) {
                        style = "border-dao-paper-darker hover:border-dao-gold/30";
                      }

                      return (
                        <button key={i} onClick={() => handleAnswer(i)}
                          disabled={quizChecked[quizIdx] !== undefined}
                          className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all tap-active ${style}`}>
                          <span className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border
                            bg-dao-paper-dark text-dao-ink-light border-dao-paper-darker">
                            {opt.label}
                          </span>
                          <span className="text-sm text-dao-ink text-left">{opt.text}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* 导师提示 */}
                  {mentorMsg && (
                    <div className="mt-3 p-3 bg-dao-indigo/5 border border-dao-indigo/20 rounded-lg">
                      <p className="text-xs text-dao-aged mb-1">导师提示</p>
                      <p className="text-sm text-dao-ink-light leading-relaxed">{mentorMsg}</p>
                    </div>
                  )}
                </div>

                {/* 导航按钮 */}
                <div className="flex justify-between">
                  <button onClick={() => { setQuizIdx(Math.max(0, quizIdx - 1)); setMentorMsg(""); }}
                    disabled={quizIdx === 0}
                    className="text-xs text-dao-indigo tap-active disabled:opacity-30">← 上一题</button>
                  {quizIdx < chapterDetail.questions.length - 1 ? (
                    <button onClick={() => { setQuizIdx(quizIdx + 1); setMentorMsg(""); }}
                      className="text-xs text-dao-indigo tap-active">下一题 →</button>
                  ) : (
                    <button onClick={finishQuiz}
                      disabled={Object.keys(quizChecked).length < chapterDetail.questions.length}
                      className="text-xs font-bold text-dao-red tap-active disabled:opacity-30">
                      提交测验 →
                    </button>
                  )}
                </div>

                {/* 错题即时提示 */}
                {quizChecked[quizIdx] === false && mentorMsg && (
                  <div className="mt-2 p-3 bg-dao-red/5 border border-dao-red/20 rounded-lg text-xs text-dao-ink-light leading-relaxed">
                    <p className="text-dao-red font-bold mb-1">回答错误，正确答案解析：</p>
                    {mentorMsg}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
