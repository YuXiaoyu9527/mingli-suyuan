"use client";

import { useState, useEffect } from "react";
import BottomNav from "@/components/BottomNav";
import { checkAnswer, askMentor } from "@/lib/api";
import { Loader2, BookOpen, ChevronRight, Lock, CheckCircle, ArrowLeft, Swords, Star, BookX, Trash2 } from "lucide-react";

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

interface WrongEntry {
  quizId: string; title: string; story: string; question: string;
  options: { label: string; text: string }[];
  userAnswer: string; correctAnswer: string; explanation: string;
  chapterId: string; chapterTitle: string;
  timestamp: string;
}

export default function XuetangPage() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [chapterDetail, setChapterDetail] = useState<ChapterDetail | null>(null);
  const [loading, setLoading] = useState(true);
  // 进度
  const [passed, setPassed] = useState<Record<string, boolean>>({});
  // 错题集
  const [wrongBook, setWrongBook] = useState<WrongEntry[]>([]);
  const [showWrongBook, setShowWrongBook] = useState(false);
  const [wrongQuizMode, setWrongQuizMode] = useState(false);
  const [devClicks, setDevClicks] = useState(0);
  const [devMode, setDevMode] = useState(false);

  const handleDevClick = () => {
    const next = devClicks + 1;
    setDevClicks(next);
    if (next >= 3) {
      setDevMode(true);
      // 解锁所有章节
      const allPassed: Record<string, boolean> = {};
      chapters.forEach(ch => { allPassed[ch.id] = true; });
      setPassed(allPassed);
      localStorage.setItem("xuetang_passed", JSON.stringify(allPassed));
    }
    setTimeout(() => setDevClicks(0), 2000);
  };

  // 错题重做模式
  const startWrongQuiz = () => {
    if (wrongBook.length === 0) return;
    // 随机打乱错题
    const shuffled = [...wrongBook].sort(() => Math.random() - 0.5);
    // 构建虚拟章节
    setChapterDetail({
      id: "wrong-retry",
      title: "错题重做",
      subtitle: `随机${shuffled.length}道错题`,
      pass_score: Math.ceil(shuffled.length * 0.7),
      content: [],
      questions: shuffled.map(w => ({
        id: w.quizId,
        title: w.title,
        difficulty: 1,
        story: w.story,
        question: w.question,
        options: w.options || [],
      })),
    });
    setWrongQuizMode(true);
    setQuizMode(true);
    setQuizIdx(0);
    setQuizAnswers({});
    setQuizChecked({});
    setQuizCorrectText({});
    setQuizResult(null);
    setMentorMsg("");
  };
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
    const wrong = localStorage.getItem("xuetang_wrong_book");
    if (wrong) setWrongBook(JSON.parse(wrong));
    loadChapters();
  }, []);

  const saveWrongBook = (entries: WrongEntry[]) => {
    setWrongBook(entries);
    localStorage.setItem("xuetang_wrong_book", JSON.stringify(entries));
  };

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
        // 加入错题集
        const entry: WrongEntry = {
          quizId: q.id, title: q.title, story: q.story, question: q.question,
          options: q.options,
          userAnswer: q.options[optIdx].text,
          correctAnswer: result.correct_text || "",
          explanation: result.analysis || result.classical_ref || "",
          chapterId: chapterDetail!.id, chapterTitle: chapterDetail!.title,
          timestamp: new Date().toISOString(),
        };
        // 去重：同题只保留最新一次
        const updated = wrongBook.filter(w => w.quizId !== q.id);
        saveWrongBook([entry, ...updated]);

        try {
          const mentor = await askMentor(
            `${q.story}\n\n${q.question}`,
            q.options[optIdx].text,
            result.correct_text || q.options[result.correct_answer]?.text || "",
          );
          setMentorMsg(mentor.hint || "");
        } catch {}
      } else {
        // 答对了，从错题集移除
        const updated = wrongBook.filter(w => w.quizId !== q.id);
        if (updated.length < wrongBook.length) saveWrongBook(updated);
        setMentorMsg("");
      }
    } catch {}
  };

  const finishQuiz = () => {
    const total = chapterDetail!.questions.length;
    const answered = Object.keys(quizChecked).length;
    const correct = Object.values(quizChecked).filter(Boolean).length;
    // 未答的题算错
    const wrongCount = (total - answered) + (answered - correct);
    const passed_quiz = answered === total && correct >= chapterDetail!.pass_score;

    setQuizResult({ correct, total, passed: passed_quiz });

    if (passed_quiz && !wrongQuizMode) {
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl text-text font-[family-name:var(--font-display)] tracking-wider"
                onClick={handleDevClick}>
                命理学堂
                {devMode && <span className="text-xs text-gold ml-2 font-normal">[已解锁]</span>}
              </h1>
              <p className="text-text-secondary text-sm mt-1">
                从零学八字 · 教材+测验 · 通关解锁
                {devMode && <span className="text-gold ml-1">· 开发者模式</span>}
              </p>
            </div>
            {wrongBook.length > 0 && (
              <button onClick={() => setShowWrongBook(!showWrongBook)}
                className="relative flex items-center gap-1 px-3 py-1.5 bg-accent/10 text-accent
                           rounded-full text-xs font-medium tap-active border border-accent/20">
                <BookX size={14} />
                错题集
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent text-white text-[10px]
                               rounded-full flex items-center justify-center">{wrongBook.length}</span>
              </button>
            )}
          </div>
        </header>

        <div className="px-5 flex-1 space-y-3">
          {loading && (
            <div className="flex justify-center py-12">
              <Loader2 size={28} className="animate-spin text-gold" />
            </div>
          )}

          {/* 错题集视图 */}
          {showWrongBook && (
            <div className="dao-card mb-3 anim-enter">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-text flex items-center gap-2">
                  <BookX size={16} className="text-accent" /> 我的错题集
                </h3>
                <button onClick={() => { saveWrongBook([]); }}
                  className="text-[10px] text-text-secondary tap-active flex items-center gap-1">
                  <Trash2 size={11} /> 清空
                </button>
              </div>

              {wrongBook.length === 0 ? (
                <p className="text-xs text-text-secondary text-center py-4">暂无错题，继续保持！</p>
              ) : (
                <div className="space-y-2 max-h-[50vh] overflow-y-auto">
                  {wrongBook.map((w, i) => (
                    <div key={i} className="border border-border rounded-lg p-3">
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-xs font-bold text-text">{w.title}</span>
                        <span className="text-[10px] text-text-tertiary">{w.chapterTitle}</span>
                      </div>
                      {/* 情景还原 */}
                      <p className="text-[11px] text-text leading-relaxed mb-2 whitespace-pre-line">{w.story}</p>
                      {/* 原问题 */}
                      <p className="text-[11px] text-text font-medium mb-2">❓ {w.question}</p>
                      {/* 答题对比 */}
                      <div className="grid grid-cols-2 gap-2 mb-2 text-[10px]">
                        <div className="bg-accent/5 rounded p-1.5 border border-accent/20">
                          <span className="text-accent">你的回答</span>
                          <p className="text-accent font-medium mt-0.5">{w.userAnswer}</p>
                        </div>
                        <div className="bg-green/5 rounded p-1.5 border border-green/20">
                          <span className="text-green">正确答案</span>
                          <p className="text-green font-medium mt-0.5">{w.correctAnswer}</p>
                        </div>
                      </div>
                      {/* 问题解析 */}
                      {w.explanation && (
                        <div className="bg-bg-subtle/50 rounded p-2 text-[10px] text-text leading-relaxed border-l-2 border-gold">
                          <span className="text-gold font-medium">解析：</span>
                          {w.explanation}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              <div className="flex gap-2 mt-3">
                <button onClick={() => {
                  setShowWrongBook(false);
                  startWrongQuiz();
                }}
                  className="flex-1 py-2 bg-accent text-white rounded-lg text-xs font-medium tap-active">
                  开始重做错题（{wrongBook.length}题）
                </button>
                <button onClick={() => setShowWrongBook(false)}
                  className="px-4 py-2 bg-bg-subtle rounded-lg text-xs tap-active">
                  收起
                </button>
              </div>
            </div>
          )}

          {chapters.map((ch) => {
            const unlocked = isUnlocked(ch);
            return (
              <button key={ch.id} disabled={!unlocked}
                onClick={() => loadChapter(ch.id)}
                className={`w-full text-left dao-card tap-active transition-all
                  ${!unlocked ? "opacity-50" : "hover:border-gold/50"}`}>
                <div className="flex items-center gap-4">
                  {/* 图标 */}
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
                    ${passed[ch.id] ? "bg-green/20 text-green" :
                      unlocked ? "bg-gold/10 text-gold" : "bg-bg-subtle text-text-secondary"}`}>
                    {passed[ch.id] ? <CheckCircle size={22} /> :
                     unlocked ? <BookOpen size={22} /> : <Lock size={22} />}
                  </div>
                  {/* 信息 */}
                  <div className="flex-1">
                    <h3 className="text-base font-bold text-text">{ch.title}</h3>
                    <p className="text-xs text-text-secondary mt-0.5">{ch.subtitle}</p>
                    <div className="flex items-center gap-3 mt-1.5 text-[11px] text-text-tertiary">
                      <span>{ch.question_count}道情景题</span>
                      <span>正确{ch.pass_score}题即通关</span>
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-text-secondary" />
                </div>
                {/* 进度条 */}
                {passed[ch.id] && (
                  <div className="mt-3 h-1 bg-green/20 rounded-full overflow-hidden">
                    <div className="h-full bg-green w-full rounded-full" />
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
          <button onClick={() => { setChapterDetail(null); setWrongQuizMode(false); }}
            className="text-text-secondary tap-active"><ArrowLeft size={20} /></button>
          <div className="flex-1">
            <h1 className="text-lg font-[family-name:var(--font-display)] text-text">
              {chapterDetail.title}
            </h1>
          </div>
          <button onClick={() => setQuizMode(!quizMode)}
            className={`text-xs px-3 py-1.5 rounded-full tap-active border
              ${quizMode ? "bg-accent text-white border-accent" : "bg-bg-subtle text-text border-border"}`}>
            {quizMode ? "← 回教材" : "开始测验 →"}
          </button>
          {wrongBook.length > 0 && (
            <button onClick={() => { setChapterDetail(null); setShowWrongBook(true); }}
              className="relative text-xs px-2 py-1 bg-accent/10 text-accent rounded-full tap-active">
              <BookX size={13} /> {wrongBook.length}
            </button>
          )}
        </div>
        {/* 总进度 */}
        <div className="mt-2 flex items-center gap-2 text-[11px] text-text-secondary">
          <span>学习进度：{totalProgress}/{totalChapters}章</span>
          <div className="flex-1 h-1 bg-bg-subtle rounded-full overflow-hidden">
            <div className="h-full bg-gold rounded-full" style={{width: `${(totalProgress/totalChapters)*100}%`}} />
          </div>
        </div>
      </header>

      <div className="px-5 flex-1">
        {!quizMode ? (
          // ===== 阅读模式 =====
          <div className="space-y-4 anim-enter">
            {chapterDetail.content.map((block, i) => {
              if (block.type === "heading") {
                return <h2 key={i} className="text-lg font-bold text-text mt-6 mb-2 font-[family-name:var(--font-display)]">{block.text}</h2>;
              }
              if (block.type === "quote") {
                return (
                  <div key={i} className="classical-quote text-sm">
                    <p>{block.text}</p>
                    {block.source && <p className="text-[10px] text-text-secondary mt-2">—— {block.source}</p>}
                  </div>
                );
              }
              return <p key={i} className="text-sm text-text leading-relaxed">{block.text}</p>;
            })}

            {/* 进入测验按钮 */}
            <div className="py-6 text-center">
              <button onClick={() => setQuizMode(true)}
                className="btn-dao flex items-center gap-2 mx-auto">
                <Swords size={16} /> 开始测验（{chapterDetail.questions.length}题）
              </button>
              <p className="text-[11px] text-text-secondary mt-2">正确{chapterDetail.pass_score}题即可通关</p>
            </div>
          </div>
        ) : quizResult ? (
          // ===== 测验结果 + 错题回顾 =====
          <div className="anim-enter space-y-4">
            {/* 分数卡片 */}
            <div className="text-center py-8 space-y-4">
              <div className={`w-20 h-20 rounded-full mx-auto flex items-center justify-center
                ${quizResult.passed ? "bg-green/20" : "bg-accent/10"}`}>
                <span className={`text-3xl font-bold ${quizResult.passed ? "text-green" : "text-accent"}`}>
                  {quizResult.correct}/{quizResult.total}
                </span>
              </div>
              <h2 className={`text-xl font-bold ${quizResult.passed ? "text-green" : "text-accent"}`}>
                {quizResult.passed ? "恭喜通关！" : Object.keys(quizChecked).length < chapterDetail!.questions.length ? "提前退出" : "还需努力"}
              </h2>
              <p className="text-sm text-text-secondary">
                {wrongQuizMode
                  ? `错题重做完成！${quizResult.passed ? "错误都已纠正" : "还有错题需要巩固"}`
                  : quizResult.passed
                    ? "下一章已解锁，继续学习吧！"
                    : Object.keys(quizChecked).length < chapterDetail!.questions.length
                      ? `已答${Object.keys(quizChecked).length}题，对${quizResult.correct}题。需要全部答完且正确${chapterDetail.pass_score}题才能通关`
                      : `需要正确${chapterDetail.pass_score}题才能通关`}
              </p>
            </div>

            {/* 逐题回顾 */}
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-text">答题回顾</h3>
              {chapterDetail.questions.map((q, i) => {
                const isRight = quizChecked[i] === true;
                const isWrong = quizChecked[i] === false;
                const userAnswer = quizAnswers[i];
                const userOption = userAnswer !== undefined ? q.options[userAnswer].text : "未作答";
                return (
                  <div key={i} className={`dao-card py-3 px-4 ${isRight ? "border-l-2 border-l-dao-jade" : isWrong ? "border-l-2 border-l-dao-red" : ""}`}>
                    <div className="flex items-start gap-2">
                      <span className={`text-xs font-bold mt-0.5 flex-shrink-0 ${isRight ? "text-green" : isWrong ? "text-accent" : "text-text-secondary"}`}>
                        {isRight ? "✓" : isWrong ? "✗" : "○"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-bold text-text">{q.title}</p>
                        <p className="text-[11px] text-text leading-relaxed mt-1 line-clamp-3">{q.story}</p>
                        <p className="text-[10px] text-text-secondary mt-1">❓ {q.question}</p>
                        <p className="text-[11px] text-text-secondary mt-1">你的回答：{userOption}</p>
                        {isWrong && quizCorrectText[i] && (
                          <>
                            <p className="text-[11px] text-green mt-0.5 font-medium">正确答案：{quizCorrectText[i]}</p>
                            {(() => {
                              const wb = wrongBook.find(w => w.quizId === q.id);
                              if (wb?.explanation) {
                                return (
                                  <p className="text-[10px] text-gold-dark mt-1 leading-relaxed bg-bg-subtle/50 rounded p-1.5">
                                    {wb.explanation}
                                  </p>
                                );
                              }
                              return null;
                            })()}
                          </>
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
                  if (wrongQuizMode) startWrongQuiz();
                  else { setQuizMode(true); setQuizIdx(0); setQuizAnswers({}); setQuizChecked({}); setQuizCorrectText({}); setQuizResult(null); setMentorMsg(""); }
                }} className="px-4 py-2 bg-accent text-white rounded-lg text-sm tap-active">
                  {wrongQuizMode ? "再做一遍错题" : "重新测验"}
                </button>
              )}
              <button onClick={() => {
                if (wrongQuizMode) { setChapterDetail(null); setWrongQuizMode(false); }
                else { setQuizMode(false); setQuizIdx(0); }
                setQuizAnswers({}); setQuizChecked({}); setQuizCorrectText({}); setQuizResult(null); setMentorMsg("");
              }} className="px-4 py-2 bg-bg-subtle rounded-lg text-sm tap-active">
                {wrongQuizMode ? "返回学堂" : "回教材再看一遍"}
              </button>
            </div>
          </div>
        ) : (
          // ===== 测验模式 =====
          <div className="space-y-4 anim-enter">
            {/* 进度 */}
            <div className="flex items-center justify-between text-xs text-text-secondary">
              <span>第 {quizIdx + 1}/{chapterDetail.questions.length} 题</span>
              <div className="flex gap-1">
                {chapterDetail.questions.map((_, i) => (
                  <div key={i} className={`w-2 h-2 rounded-full
                    ${quizChecked[i] === true ? "bg-green" :
                      quizChecked[i] === false ? "bg-accent" :
                      quizAnswers[i] !== undefined ? "bg-gold" : "bg-bg-subtleer"}`} />
                ))}
              </div>
              <span className="text-gold">
                已对 {Object.values(quizChecked).filter(Boolean).length} 题
              </span>
            </div>

            {q && (
              <>
                {/* 题目 */}
                <div className="dao-card">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-text-secondary">{q.title}</span>
                    <span className="flex gap-0.5">
                      {[1,2,3].map(d => <Star key={d} size={10} className={d <= q.difficulty ? "fill-dao-gold text-gold" : "text-dao-paper-darker"} />)}
                    </span>
                  </div>
                  <p className="text-sm text-text leading-relaxed whitespace-pre-line">{q.story}</p>
                </div>

                {/* 问题 */}
                <div className="dao-card" style={{ borderColor: "rgba(201,169,110,0.3)" }}>
                  <p className="text-sm font-bold text-text mb-3">❓ {q.question}</p>
                  <div className="space-y-2">
                    {q.options.map((opt, i) => {
                      const checked = quizChecked[quizIdx];
                      const isSelected = quizAnswers[quizIdx] === i;
                      let style = "border-border";
                      if (checked !== undefined && isSelected) {
                        style = checked ? "border-green bg-green/5" : "border-accent bg-accent/5";
                      } else if (!isSelected) {
                        style = "border-border hover:border-gold/30";
                      }

                      return (
                        <button key={i} onClick={() => handleAnswer(i)}
                          disabled={quizChecked[quizIdx] !== undefined}
                          className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all tap-active ${style}`}>
                          <span className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border
                            bg-bg-subtle text-text border-border">
                            {opt.label}
                          </span>
                          <span className="text-sm text-text text-left">{opt.text}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* 导师提示 */}
                  {mentorMsg && (
                    <div className="mt-3 p-3 bg-dao-indigo/5 border border-dao-indigo/20 rounded-lg">
                      <p className="text-xs text-text-secondary mb-1">导师提示</p>
                      <p className="text-sm text-text leading-relaxed">{mentorMsg}</p>
                    </div>
                  )}
                </div>

                {/* 导航按钮 */}
                <div className="flex justify-between">
                  <button onClick={() => { setQuizIdx(Math.max(0, quizIdx - 1)); setMentorMsg(""); }}
                    disabled={quizIdx === 0}
                    className="text-xs text-accent tap-active disabled:opacity-30">← 上一题</button>
                  {quizIdx < chapterDetail.questions.length - 1 ? (
                    <button onClick={() => { setQuizIdx(quizIdx + 1); setMentorMsg(""); }}
                      className="text-xs text-accent tap-active">下一题 →</button>
                  ) : (
                    <button onClick={finishQuiz}
                      disabled={Object.keys(quizChecked).length < chapterDetail.questions.length}
                      className="text-xs font-bold text-accent tap-active disabled:opacity-30">
                      提交测验 →
                    </button>
                  )}
                </div>

                {/* 提前退出按钮 */}
                {Object.keys(quizAnswers).length > 0 && !quizResult && (
                  <div className="text-center mt-3">
                    <button onClick={finishQuiz}
                      className="text-[11px] text-text-tertiary tap-active hover:text-accent transition-colors">
                      提前退出（已答{Object.keys(quizChecked).length}/{chapterDetail.questions.length}题）
                    </button>
                  </div>
                )}

                {/* 错题即时提示 */}
                {quizChecked[quizIdx] === false && mentorMsg && (
                  <div className="mt-2 p-3 bg-accent/5 border border-accent/20 rounded-lg text-xs text-text leading-relaxed">
                    <p className="text-accent font-bold mb-1">回答错误，正确答案解析：</p>
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
